import re


def process_text_file(input_file, output_sql_file, table_name):
    """
    Process the input text file and generate SQL for upserting data to Supabase

    Args:
        input_file (str): Path to the input text file
        output_sql_file (str): Path to save the generated SQL file
        table_name (str): Name of the table in Supabase
    """

    # Read the input file
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    # Parse names and emails
    data = []
    current_name = None

    for line in lines:
        if not line.strip():  # Skip empty lines
            continue

        # If current_name is None, this is a name line
        if current_name is None:
            current_name = line
        else:
            # This is an email line (assuming format is consistent)
            email = line
            data.append((current_name, email))
            current_name = None

    # Generate SQL
    sql_lines = [
        f"-- SQL script for upserting data to {table_name} table",
        f"-- Generated from {input_file}",
        "",
        f"-- Create table if not exists",
        f"CREATE TABLE IF NOT EXISTS {table_name} (",
        "    id SERIAL PRIMARY KEY,",
        "    name TEXT NOT NULL,",
        "    email TEXT NOT NULL UNIQUE,",
        "    created_at TIMESTAMPTZ DEFAULT NOW(),",
        "    updated_at TIMESTAMPTZ DEFAULT NOW()",
        ");",
        "",
        "-- Create trigger for updated_at",
        f"CREATE OR REPLACE FUNCTION update_{table_name}_modtime()",
        "RETURNS TRIGGER AS $$",
        "BEGIN",
        "    NEW.updated_at = NOW();",
        "    RETURN NEW;",
        "END;",
        "$$ LANGUAGE plpgsql;",
        "",
        f"DROP TRIGGER IF EXISTS update_{table_name}_modtime ON {table_name};",
        "",
        f"CREATE TRIGGER update_{table_name}_modtime",
        f"BEFORE UPDATE ON {table_name}",
        "FOR EACH ROW",
        f"EXECUTE FUNCTION update_{table_name}_modtime();",
        "",
        "-- Upsert data",
        f"INSERT INTO {table_name} (name, email)",
        "VALUES"
    ]

    # Add values
    value_lines = []
    for name, email in data:
        value_lines.append(f"    ('{name.replace("'", "''")}', '{email.replace("'", "''")}')")

    sql_lines.append(",\n".join(value_lines))

    # Add ON CONFLICT clause for upsert
    sql_lines.append(f"ON CONFLICT (email) DO UPDATE SET")
    sql_lines.append("    name = EXCLUDED.name,")
    sql_lines.append("    updated_at = NOW();")

    # Write SQL to file
    with open(output_sql_file, 'w') as f:
        f.write("\n".join(sql_lines))

    print(f"SQL script generated successfully at {output_sql_file}")


if __name__ == "__main__":
    # Configuration
    input_file = "employees.txt"  # Change to your input file path
    output_sql_file = "upsert_employees.sql"  # Output SQL file
    table_name = "employees"  # Supabase table name

    process_text_file(input_file, output_sql_file, table_name)
import os
import re


def generate_email_groups_sql(input_directory, output_sql_file):
    """
    Generate SQL script for uploading email-group relationships to Supabase.

    Args:
        input_directory (str): Directory containing group files (filenames = group names)
        output_sql_file (str): Path to save the generated SQL file
    """

    # Dictionary to store email-group relationships
    email_groups = {}

    # Process each file in the input directory
    for filename in os.listdir(input_directory):
        if not os.path.isfile(os.path.join(input_directory, filename)):
            continue

        group_name = os.path.splitext(filename)[0]

        with open(os.path.join(input_directory, filename), 'r') as f:
            for line in f:
                email = line.strip()
                if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    continue

                if email not in email_groups:
                    email_groups[email] = []
                if group_name not in email_groups[email]:
                    email_groups[email].append(group_name)

    # Generate SQL
    sql_lines = [
        "-- SQL script for uploading email-group relationships",
        "-- Generated from files in: " + input_directory,
        "",
        "-- Create tables if they don't exist",
        "CREATE TABLE IF NOT EXISTS emails (",
        "    id SERIAL PRIMARY KEY,",
        "    email TEXT NOT NULL UNIQUE,",
        "    created_at TIMESTAMPTZ DEFAULT NOW()",
        ");",
        "",
        "CREATE TABLE IF NOT EXISTS groups (",
        "    id SERIAL PRIMARY KEY,",
        "    name TEXT NOT NULL UNIQUE,",
        "    created_at TIMESTAMPTZ DEFAULT NOW()",
        ");",
        "",
        "CREATE TABLE IF NOT EXISTS email_groups (",
        "    email_id INTEGER NOT NULL REFERENCES emails(id) ON DELETE CASCADE,",
        "    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,",
        "    created_at TIMESTAMPTZ DEFAULT NOW(),",
        "    PRIMARY KEY (email_id, group_id)",
        ");",
        "",
        "-- Insert or ignore groups",
        "INSERT INTO groups (name)",
        "VALUES"
    ]

    # Get all unique group names
    all_groups = set()
    for groups in email_groups.values():
        all_groups.update(groups)

    # Add group values
    group_values = []
    for group in sorted(all_groups):
        group_values.append(f"    ('{group.replace("'", "''")}')")

    sql_lines.append(",\n".join(group_values))
    sql_lines.append("ON CONFLICT (name) DO NOTHING;")
    sql_lines.append("")

    # Insert or ignore emails
    sql_lines.append("-- Insert or ignore emails")
    sql_lines.append("INSERT INTO emails (email)")
    sql_lines.append("VALUES")

    # Add email values
    email_values = []
    for email in sorted(email_groups.keys()):
        email_values.append(f"    ('{email.replace("'", "''")}')")

    sql_lines.append(",\n".join(email_values))
    sql_lines.append("ON CONFLICT (email) DO NOTHING;")
    sql_lines.append("")

    # Insert email-group relationships using a more compatible approach
    sql_lines.append("-- Insert email-group relationships")
    sql_lines.append("DO $$")
    sql_lines.append("BEGIN")

    # For each email-group pair, create an insert statement
    for email, groups in email_groups.items():
        for group in groups:
            sql_lines.append(
                f"    INSERT INTO email_groups (email_id, group_id) "
                f"SELECT e.id, g.id FROM emails e, groups g "
                f"WHERE e.email = '{email.replace("'", "''")}' "
                f"AND g.name = '{group.replace("'", "''")}' "
                "ON CONFLICT (email_id, group_id) DO NOTHING;"
            )

    sql_lines.append("END $$;")

    # Write SQL to file
    with open(output_sql_file, 'w') as f:
        f.write("\n".join(sql_lines))

    print(f"SQL script generated successfully at {output_sql_file}")
    print(f"Processed {len(email_groups)} emails and {len(all_groups)} groups")


if __name__ == "__main__":
    # Configuration
    input_directory = "email_groups"  # Directory containing group files
    output_sql_file = "upload_email_groups.sql"  # Output SQL file

    generate_email_groups_sql(input_directory, output_sql_file)
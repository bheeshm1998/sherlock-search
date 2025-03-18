# import crewai
#
# # Define Agent Roles
# class Researcher(crewai.Agent):
#     def act(self, topic):
#         return f"Researching the latest trends and information on {topic}."
#
# class Writer(crewai.Agent):
#     def act(self, research):
#         return f"Writing an article based on the research: {research}."
#
# class Editor(crewai.Agent):
#     def act(self, article):
#         return f"Reviewing and editing the article: {article}."
#
# class Publisher(crewai.Agent):
#     def act(self, edited_article):
#         return f"Publishing the final version: {edited_article}."
#
# # Instantiate Agents
# researcher = Researcher()
# writer = Writer()
# editor = Editor()
# publisher = Publisher()
#
# def run_pipeline(topic):
#     research = researcher.act(topic)
#     article = writer.act(research)
#     edited_article = editor.act(article)
#     final_output = publisher.act(edited_article)
#     return final_output
#
# # Run the Multi-Agent Workflow
# topic = "Future of AI in Healthcare"
# output = run_pipeline(topic)
# print(output)

import openai
import os

openai.api_key = os.environ.get("openai_key")
sy="You are expert in resume buider for graduate."
pre_experience=""""
in a resume preexisting experience field contains below data.

{experience}

Please change this experience according to below job description quoted in @@@, provide output in the above format only without any labelling or formating.
@@@
{data}
@@@
"""

resumePrompt="""
in a resume preexisting {preData} contains below data.

{data}

Please change this {preData} according to below job description quoted in @@@, provide output in the above format only without any labelling or formating.
@@@
{job_role}
@@@
"""
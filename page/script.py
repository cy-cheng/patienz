import asyncio
import sys
from model.grader import create_grader_model
from model.advisor import create_advisor_model

async def get_grading_result_async(current_model, messages_for_grading):
    grader = current_model.start_chat()
    response = await grader.send_message_async(messages_for_grading)
    return response.text

async def main():
    grader_models = sys.argv[1]
    messages = sys.argv[2]
    tasks = [get_grading_result_async(model, msg) for model, msg in zip(grader_models, messages)]
    results = await asyncio.gather(*tasks)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
    

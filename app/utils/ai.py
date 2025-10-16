"""
AI Integration utilities
OpenAI for smart task generation
"""

import openai
from flask import current_app
import json


def generate_task_from_prompt(prompt):
    """Generate task card from AI prompt"""
    try:
        api_key = current_app.config.get('OPENAI_API_KEY')
        
        if not api_key:
            # Return mock data if API key not configured
            return generate_mock_task(prompt)
        
        openai.api_key = api_key
        
        system_message = """
        You are an AI assistant that helps create structured task cards for project management.
        Given a description or meeting notes, extract and create a task with:
        - Title (short, actionable)
        - Description (detailed)
        - Deliverables (list of specific outcomes)
        - Priority (low, medium, high, urgent)
        - Estimated hours
        
        Return ONLY a valid JSON object with these fields.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Create a task from: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        task_json = response.choices[0].message.content
        task_data = json.loads(task_json)
        
        return task_data
        
    except Exception as e:
        current_app.logger.error(f"AI task generation error: {e}")
        return generate_mock_task(prompt)


def generate_mock_task(prompt):
    """Generate a mock task when AI is not available"""
    return {
        'title': 'New Task from AI',
        'description': f'Generated from prompt: {prompt[:200]}',
        'deliverables': [
            {'text': 'Review requirements', 'completed': False},
            {'text': 'Complete implementation', 'completed': False},
            {'text': 'Test and deploy', 'completed': False}
        ],
        'priority': 'medium',
        'estimated_hours': 8
    }


def summarize_text(text, max_length=200):
    """Summarize long text using AI"""
    try:
        api_key = current_app.config.get('OPENAI_API_KEY')
        
        if not api_key or len(text) < max_length:
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following text concisely."},
                {"role": "user", "content": text}
            ],
            temperature=0.5,
            max_tokens=100
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        current_app.logger.error(f"AI summarization error: {e}")
        return text[:max_length] + ('...' if len(text) > max_length else '')


def suggest_task_priority(task_description, due_date=None):
    """Suggest task priority based on description and due date"""
    try:
        api_key = current_app.config.get('OPENAI_API_KEY')
        
        if not api_key:
            return 'medium'
        
        openai.api_key = api_key
        
        prompt = f"Task: {task_description}"
        if due_date:
            prompt += f"\nDue date: {due_date}"
        
        prompt += "\n\nBased on this task, suggest a priority level (low, medium, high, or urgent). Respond with ONLY one word."
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a project management assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10
        )
        
        priority = response.choices[0].message.content.strip().lower()
        
        if priority in ['low', 'medium', 'high', 'urgent']:
            return priority
        return 'medium'
        
    except Exception as e:
        current_app.logger.error(f"AI priority suggestion error: {e}")
        return 'medium'


def extract_action_items(meeting_notes):
    """Extract action items from meeting notes"""
    try:
        api_key = current_app.config.get('OPENAI_API_KEY')
        
        if not api_key:
            return []
        
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "Extract action items from meeting notes. Return as a JSON array of objects with 'task' and 'assignee' fields."
                },
                {"role": "user", "content": meeting_notes}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        items_json = response.choices[0].message.content
        action_items = json.loads(items_json)
        
        return action_items
        
    except Exception as e:
        current_app.logger.error(f"AI action item extraction error: {e}")
        return []

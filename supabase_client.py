from supabase import create_client, Client
import os
from typing import Dict, Any, Optional
import json

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")

supabase: Client = create_client(supabase_url, supabase_key)

def save_note(note_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Save a note to the Supabase database.
    
    Args:
        note_data (Dict[str, Any]): The note data to save
        
    Returns:
        Optional[Dict[str, Any]]: The saved note data if successful, None otherwise
    """
    try:
        # Convert summary array to formatted text
        if 'summary' in note_data and isinstance(note_data['summary'], list):
            summary_array = note_data['summary']
            if len(summary_array) >= 1:
                # First element is the one-sentence summary
                one_sentence = summary_array[0]
                
                # Next 10 elements are main points
                main_points = summary_array[1:11] if len(summary_array) > 1 else []
                
                # Last 5 elements are takeaways
                takeaways = summary_array[11:16] if len(summary_array) > 11 else []
                
                # Format the summary text
                formatted_summary = f"{one_sentence}\n\nMain Points:\n"
                formatted_summary += "\n".join(f"- {point}" for point in main_points)
                formatted_summary += "\n\nKey Takeaways:\n"
                formatted_summary += "\n".join(f"- {takeaway}" for takeaway in takeaways)
                
                # Update the note_data with the formatted summary
                note_data['summary'] = formatted_summary
            
        # Ensure source_type is valid
        valid_source_types = {'file', 'youtube', 'audio', 'text', 'live'}
        if note_data.get('source_type') not in valid_source_types:
            raise ValueError(f"Invalid source_type. Must be one of: {valid_source_types}")
            
        # Insert the note into the 'notes' table
        response = supabase.table('notes').insert(note_data).execute()
        
        if response.data and len(response.data) > 0:
            print("Successfully saved note to Supabase")
            return response.data[0]
        else:
            print("Failed to save note: No data returned from Supabase")
            return None
            
    except Exception as e:
        print(f"Error saving note to Supabase: {e}")
        return None

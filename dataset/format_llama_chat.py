import re
import random
import json
from datasets import Dataset

# Special tokens for Llama chat format
BOS = "<s>"
EOS = "</s>"
INST = "[INST]"
INST_END = "[/INST]"
SYS = "<<SYS>>"
SYS_END = "<</SYS>>"

# Jack's characteristic phrases and responses
JACK_PHRASES = [
    "Savvy?",
    "Why is the rum gone?",
    "Aye?",
    "Parley?",
    "Captain Jack Sparrow, if you please.",
    "Ah, but you have heard of me.",
    "Not all treasure is silver and gold, mate.",
    "The only rules that really matter are these: what a man can do and what a man can't do.",
    "I'm dishonest, and a dishonest man you can always trust to be dishonest.",
    "This is the day you will always remember as the day you almost caught Captain Jack Sparrow!",
    "Drink up me hearties, yo ho!",
    "The Black Pearl is freedom.",
    "I love those moments. I like to wave at them as they pass by.",
    "Not probable.",
    "Complications arose, ensued, were overcome.",
    "I'm Captain Jack Sparrow. Savvy?",
    "The code is more what you'd call guidelines than actual rules.",
    "I'm not sure I deserve this, but I have it, and I aim to keep it.",
    "The only way a pirate can make a living these days is by betraying other pirates.",
    "I'm in the market, as it were.",
]

# Various prompts to add context
PROMPTS = [
    "What do you think about that?",
    "How do you feel about this situation?",
    "What's your plan?",
    "What do you make of this?",
    "How do you propose we proceed?",
    "What's your take on this?",
    "What do you suggest?",
    "How do you see this playing out?",
    "What's your opinion on this matter?",
    "How do you intend to handle this?",
    "What's your strategy?",
    "How do you plan to get out of this?",
    "What's your next move?",
    "How do you propose we solve this?",
    "What's your assessment of the situation?",
]

# Contextual situations
CONTEXTS = [
    "On the Black Pearl",
    "In Tortuga",
    "During a battle",
    "While negotiating",
    "When planning an escape",
    "During a treasure hunt",
    "When facing danger",
    "While making a deal",
    "During a mutiny",
    "When meeting new people",
    "While being chased",
    "When making a plan",
    "During a storm",
    "When in trouble",
    "While seeking revenge",
]

def is_valid_dialogue(line):
    """Check if the line is valid dialogue."""
    # Skip lines with numbers or citations
    if re.search(r'\d+', line):
        return False
        
    # Skip lines with URLs or web references
    if re.search(r'http|www|\.com|\.org|\.net', line, re.IGNORECASE):
        return False
        
    # Skip lines with academic citations
    if re.search(r'\[\d+\]|\(\d+\)', line):
        return False
        
    # Skip lines that look like Wikipedia content
    if re.search(r'According to|In the|The|After|Before|During|While', line, re.IGNORECASE):
        return False
        
    # Skip lines that are too formal or academic
    if re.search(r'Furthermore|Moreover|However|Therefore|Thus|Hence', line, re.IGNORECASE):
        return False
        
    return True

def format_sharegpt(input_file, output_file):
    """
    Format the dialogue data in ShareGPT format.
    
    Args:
        input_file (str): Path to the raw dialogue file
        output_file (str): Path to save the formatted dialogue
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    conversations = []

    # Process lines in pairs
    i = 0
    while i < len(lines):
        # Skip empty lines
        while i < len(lines) and not lines[i].strip():
            i += 1
            
        if i >= len(lines):
            break
            
        # Get the human prompt (first line)
        human_line = lines[i].strip()
        i += 1
        
        # Skip empty lines between prompt and response
        while i < len(lines) and not lines[i].strip():
            i += 1
            
        if i >= len(lines):
            break
            
        # Get Jack's response (second line)
        jack_line = lines[i].strip()
        i += 1
        
        # Create conversation in ShareGPT format
        conversation = {
            "id": f"jack_{len(conversations)}",
            "conversations": [
                {
                    "from": "human",
                    "value": human_line
                },
                {
                    "from": "assistant",
                    "value": jack_line
                }
            ],
        }
        conversations.append(conversation)
    
    # Save as JSONL file
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for conversation in conversations:
            json.dump(conversation, out_file, ensure_ascii=False)
            out_file.write('\n')

    print(f"✅ Saved {len(conversations)} ShareGPT-style conversations to {output_file}")

if __name__ == "__main__":
    input_file = "..\\res\\jack_llama_all_text.txt"
    output_file = "..\\res\\jack_sharegpt_dataset.jsonl"
    format_sharegpt(input_file, output_file) 
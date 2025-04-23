import re
import pdfplumber
import os
import glob

def extract_jack_sparrow_lines(filepath, output_path):
    """
    Extract Jack Sparrow's dialogue along with the previous line from another character.
    Returns a list of tuples (previous_line, jack_line).
    """
    dialogue_pairs = []
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    is_jack_talking = False
    previous_lines = []
    jack_lines = []
    current_character = None
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines unless we're in the middle of collecting dialogue
        if not stripped and not (previous_lines or jack_lines):
            continue
            
        # Check if this is a character name (all caps and not too long)
        if stripped.isupper() and len(stripped) < 30 and not any(c in stripped for c in '.,!?'):
            if stripped == "JACK" or stripped == "JACK SPARROW":
                is_jack_talking = True
                # If we have accumulated previous lines, join them
                if previous_lines:
                    prev_text = ' '.join(previous_lines)
                    previous_lines = []
            else:
                is_jack_talking = False
                current_character = stripped
                # If we have both previous text and Jack's lines, add them as a pair
                if previous_lines and jack_lines:
                    prev_text = ' '.join(previous_lines)
                    jack_text = ' '.join(jack_lines)
                    dialogue_pairs.append((prev_text, jack_text))
                    previous_lines = []
                    jack_lines = []
            continue

        # If it's a dialogue line
        if stripped and not stripped.isupper():
            if is_jack_talking:
                jack_lines.append(stripped)
            elif current_character:  # Only collect previous lines if we have a character
                previous_lines.append(stripped)
        elif stripped == "":  # Empty line indicates end of dialogue block
            if previous_lines and jack_lines:
                prev_text = ' '.join(previous_lines)
                jack_text = ' '.join(jack_lines)
                dialogue_pairs.append((prev_text, jack_text))
                previous_lines = []
                jack_lines = []
            is_jack_talking = False
            current_character = None

    # Handle any remaining dialogue pair at the end of the file
    if previous_lines and jack_lines:
        prev_text = ' '.join(previous_lines)
        jack_text = ' '.join(jack_lines)
        dialogue_pairs.append((prev_text, jack_text))

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as out_file:
        for prev_line, jack_line in dialogue_pairs:
            out_file.write(f"{prev_line}\n{jack_line}\n\n")

    print(f"Extracted {len(dialogue_pairs)} dialogue pairs with Jack Sparrow.")

def clean_jack_line(raw_line):
    # Remove action descriptions in square brackets
    line = re.sub(r'\[.*?\]', '', raw_line)

    # Remove character name prefixes (e.g., "Jack:", "Elizabeth:")
    line = re.sub(r'^\s*\w+\s*:\s*', '', line, flags=re.IGNORECASE)

    # Fix malformed apostrophes: replace ? not at the end with '
    line = re.sub(r'\?(?=\w)', "'", line)  # '?' followed by a word character
    line = re.sub(r'\?(?!$)', "'", line)  # '?' not at the end of line

    # Clean whitespace
    line = re.sub(r'\s+', ' ', line).strip()
    return line

def process_jack_script_file(input_path, output_path):
    """
    Process the script file to extract dialogue pairs where Jack responds to another character.
    """
    dialogue_pairs = []
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
        previous_line = None

        for line in lines:
            cleaned = clean_jack_line(line)
            
            # If this is Jack's line and we have a previous line
            if "Jack : " in line and previous_line:
                # Clean the previous line
                cleaned_prev = clean_jack_line(previous_line)
                if cleaned_prev and cleaned:  # Only add if both lines are non-empty
                    dialogue_pairs.append((cleaned_prev, cleaned))
                previous_line = None
            else:
                # Store the previous line if it's not empty
                if cleaned:
                    previous_line = line

    # Write the dialogue pairs to the output file
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for prev_line, jack_line in dialogue_pairs:
            outfile.write(f"{prev_line}\n{jack_line}\n\n")

    print(f"✅ Processed {len(dialogue_pairs)} dialogue pairs to: {output_path}")

def extract_clean_jack_dialogue(pdf_path, output_path):
    """
    Extract Jack Sparrow's dialogue along with the previous line from another character from a PDF.
    """
    dialogue_pairs = []
    collecting = False
    buffer = []
    previous_lines = []
    current_character = None
    
    # Patterns to filter out
    filter_patterns = [
        r'8FLiX\.com',  # Watermark
        r'SCREENPLAY DATABASE',  # Header
        r'^\d+\.$',  # Page numbers like "113."
        r'POTC:.*\d+/\d+/\d+',  # Title and date
        r'^\d+\.\s+[A-Z]',  # Scene numbers
        r'^\d+$',  # Standalone numbers
        r'^[A-Z\s]+$',  # All caps lines that aren't character names
    ]
    
    def should_filter_line(line):
        """Check if a line should be filtered out based on patterns."""
        for pattern in filter_patterns:
            if re.search(pattern, line):
                return True
        return False
    
    print(f"Opening PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"\nProcessing page {page_num}...")
            lines = page.extract_text().split('\n')
            
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip empty lines and filtered lines unless we're in the middle of collecting dialogue
                if (not stripped or should_filter_line(stripped)) and not (previous_lines or buffer):
                    continue
                
                # Check if this is a character name (all caps and not too long)
                if stripped.isupper() and len(stripped) < 30 and not any(c in stripped for c in '.,!?'):
                    if stripped == "JACK" or stripped == "JACK SPARROW":
                        # If we have accumulated previous lines, join them
                        if previous_lines:
                            prev_text = ' '.join(previous_lines)
                            previous_lines = []
                        collecting = True
                        buffer = []
                    else:
                        # If we have both previous text and Jack's lines, add them as a pair
                        if previous_lines and buffer:
                            prev_text = ' '.join(previous_lines)
                            jack_text = ' '.join(buffer)
                            dialogue_pairs.append((prev_text, jack_text))
                            print(f"Added dialogue pair: {prev_text[:50]}... -> {jack_text[:50]}...")
                            previous_lines = []
                            buffer = []
                        collecting = False
                        current_character = stripped
                    continue

                # If it's a dialogue line
                if stripped and not stripped.isupper() and not should_filter_line(stripped):
                    if collecting:
                        buffer.append(stripped)
                    elif current_character:  # Only collect previous lines if we have a character
                        previous_lines.append(stripped)
                elif stripped == "":  # Empty line indicates end of dialogue block
                    if previous_lines and buffer:
                        prev_text = ' '.join(previous_lines)
                        jack_text = ' '.join(buffer)
                        dialogue_pairs.append((prev_text, jack_text))
                        print(f"Added dialogue pair: {prev_text[:50]}... -> {jack_text[:50]}...")
                        previous_lines = []
                        buffer = []
                    collecting = False
                    current_character = None

    # Handle any remaining dialogue pair at the end of the file
    if previous_lines and buffer:
        prev_text = ' '.join(previous_lines)
        jack_text = ' '.join(buffer)
        dialogue_pairs.append((prev_text, jack_text))
        print(f"Added final dialogue pair: {prev_text[:50]}... -> {jack_text[:50]}...")

    # Write final cleaned lines
    with open(output_path, 'w', encoding='utf-8') as out:
        for prev_line, jack_line in dialogue_pairs:
            out.write(f"{prev_line}\n{jack_line}\n\n")

    print(f"\nExtraction Summary:")
    print(f"Total dialogue pairs extracted: {len(dialogue_pairs)}")
    print(f"✅ Extracted {len(dialogue_pairs)} dialogue pairs to: {output_path}")

    return dialogue_pairs

# Example usage
# ("..\\res\\dead_men_tell_no_tales.pdf", "..\\res\\jack_gpt2_dead_men_tell_no_tales.txt")
# join_split_lines("..\\res\\jack_gpt2_dead_men_tell_no_tales.txt", "..\\res\\jack_gpt2_dead_men_tell_no_tales.txt")

def join_split_lines(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    merged_lines = []
    buffer = ""

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue  # skip empty lines

        # Check if line starts with lowercase or continuation punctuation
        if stripped[0].islower() or stripped[0] in [',', '.', '-', '\'', '"']:
            buffer += ' ' + stripped
        else:
            if buffer:
                merged_lines.append(buffer.strip())
            buffer = stripped

    # Add any remaining buffer
    if buffer:
        merged_lines.append(buffer.strip())

    # Write to output
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for line in merged_lines:
            outfile.write(line + '\n')

    print(f"Rejoined lines written to: {output_path}")

# Usage
# join_split_lines('..\\res\\jack_sparrow_lines_1.txt', '..\\res\\jack_gpt2_dead_mans_chest.txt')

def merge_jack_dialogue_files(input_dir, output_file):
    """
    Merges all files starting with 'jack_gpt2' from the input directory into a single output file.
    
    Args:
        input_dir (str): Directory containing the Jack Sparrow dialogue files
        output_file (str): Path to the output file where all dialogue will be merged
    """
    # Get all files starting with 'jack_gpt2' in the input directory
    pattern = os.path.join(input_dir, 'jack_llama_*.txt')
    files = glob.glob(pattern)
    
    if not files:
        print("No Jack Sparrow dialogue files found!")
        return
    
    # Read and merge all files
    all_lines = []
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Add a separator between files
                if all_lines:  # If not the first file
                    all_lines.append('\n')
                all_lines.extend(lines)
            print(f"✅ Added {len(lines)} lines from {os.path.basename(file)}")
        except Exception as e:
            print(f"❌ Error reading {file}: {str(e)}")
    
    # Write all lines to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(all_lines)
        print(f"✅ Successfully merged {len(files)} files into {output_file}")
        print(f"✅ Total lines: {len(all_lines)}")
    except Exception as e:
        print(f"❌ Error writing to {output_file}: {str(e)}")

# Example usage

#extract_jack_sparrow_lines("..\\res\\input.txt", "..\\res\\jack_llama_dead_man_chest.txt")
#extract_jack_sparrow_lines("..\\res\\inputPirates1.txt", "..\\res\\jack_llama_curse_of_black_pearl.txt")
#process_jack_script_file("..\\res\\inputCurseOfTheBlackPearls.txt", "..\\res\\jack_llama_curse_of_black_pearl_2.txt")

extract_clean_jack_dialogue("..\\res\\on_strager_tides.pdf", "..\\res\\jack_llama_stranger_tides.txt")
extract_clean_jack_dialogue("..\\res\\at_worlds_end.pdf", "..\\res\\jack_llama_at_worlds_end.txt")
extract_clean_jack_dialogue("..\\res\\dead_men_tell_no_tales.pdf", "..\\res\\jack_llama_dead_men_tell_no_tales.txt")
merge_jack_dialogue_files("..\\res", "..\\res\\jack_llama_all_text.txt")

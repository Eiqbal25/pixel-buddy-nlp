import json

def convert_to_instruction_format(input_file, output_file):
    print(f"🔄 Converting {input_file} to training format...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    training_data = []
    
    for item in data:
        # Create a structured prompt for the model to learn
        instruction = f"Explain the official soccer rule regarding {item['category']}."
        
        # The input adds context (source of the rule)
        input_context = f"According to {item['source']}."
        
        # The output is the actual rule content
        output_text = item['content']
        
        # Unsloth/Alpaca format
        entry = {
            "instruction": instruction,
            "input": input_context,
            "output": output_text
        }
        training_data.append(entry)
    
    # Save as JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in training_data:
            json.dump(entry, f)
            f.write('\n')
            
    print(f"✅ Success! Saved {len(training_data)} training examples to {output_file}")
    print("🚀 You can now upload this file to Google Colab.")

if __name__ == "__main__":
    convert_to_instruction_format('datasets/soccer_rules.json', 'train.jsonl')
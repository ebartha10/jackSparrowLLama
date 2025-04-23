---
tags:
- unsloth
datasets:
- Devwa/jackSparrow
language:
- en
base_model:
- meta-llama/Llama-3.2-3B-Instruct
---

# Model Card for Model ID

<!-- Provide a quick summary of what the model is/does. -->
This model is a fine tuned Llama 3.2 to behave like Jack Sparrow.


## Model Details

### Model Description

<!-- Provide a longer summary of what this model is. -->

This LLaMA model was fine-tuned on a custom dataset of Jack Sparrow's dialogue extracted from movie scripts, quotes, and paraphrased pirate-style interactions. It's designed to be used in conversational chat interfaces or roleplay environments.

- **Developed by:** [ebartha](https://github.com/ebartha10)
- **Model type:** Chat bot
- **Language(s) (NLP):** English
- **Finetuned from model [optional]:** Llama-3.2-3B-Instruct

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->

### Direct Use

This model can be used as:
- A conversational AI chatbot for fans of *Pirates of the Caribbean*
- A pirate-themed character in a storytelling game or NPC
- A personality layer on top of LLM agents (e.g., LangChain, CrewAI)



### Out-of-Scope Use
- Not suitable for factual Q&A or critical decision-making
- Should not be used to impersonate real people or used in harmful, deceptive, or offensive contexts

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

While the model is designed to be humorous and fictional, it is trained on stylized and potentially stereotypical data from movies. Users should not take responses literally or assume cultural accuracy.


### Recommendations

<!-- This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. -->

Use in entertainment, educational, or fictional settings. Always clarify that the chatbot is a fictional character, not an actual pirate or historical figure.

## How to Get Started with the Model

Use the code below to get started with the model.

[More Information Needed]

## Training Details

### Training Data

<!-- This should link to a Dataset Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. -->
The model was fine-tuned on a custom dataset of Jack Sparrow dialogue: Devwa/jackSparrow. The dataset contains over 600 carefully curated and cleaned lines of dialogue from the Pirates of the Caribbean movies, formatted in a ShareGPT-like structure. Each line is embedded in conversational context with pirate-themed prompts, randomized to improve generalization and make the model more interactive.

The data was preprocessed to remove stage directions, formal/non-character lines, and noise (e.g. web references or citations), with additional injections of characteristic Jack Sparrow phrases.

### Training Procedure

The model was fine-tuned using Unsloth's SFTTrainer, which wraps around Hugging Face's transformers and trl. The base model was meta-llama/Llama-3.2-3B-Instruct.

Training was conducted using full parameter fine-tuning with LoRA adapters. Each training sample consisted of a single formatted conversation with a user prompt and Jack Sparrow-style response.
#### Preprocessing [optional]

The dataset text field was text, with pre-formatted prompt/response structure.

Packed sequences were disabled (packing=False) to retain natural dialogue flow.

Each prompt was padded/truncated to a maximum sequence length of 2048 tokens.


#### Training Hyperparameters

- Training regime: mixed precision (fp16 if bfloat16 unsupported, bf16 otherwise)

- Epochs: 1

- Batch size: 2 (per device)

- Gradient accumulation: 4 steps (effective batch size: 8)

- Learning rate: 2e-4

- Optimizer: AdamW (8-bit)

- Weight decay: 0.01

- LR scheduler: Linear

- Warmup steps: 5

- Seed: 3407

- Output dir: outputs/
#### Speeds, Sizes, Times [optional]

<!-- This section provides information about throughput, start/end time, checkpoint size if relevant, etc. -->

PU = Tesla T4. Max memory = 14.748 GB.
2.635 GB of memory reserved.
1:36:40

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Windows 10 or higher (for the current UI implementation)
- At least 4GB of RAM
- CPU with AVX2 support (for llama.cpp)

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install torch
pip install llama-cpp-python
pip install transformers
pip install tkinter  # Usually comes with Python on Windows
```

## Model Setup

The application uses a quantized LLaMA model fine-tuned on Jack Sparrow's dialogue. The model will be automatically downloaded when you first run the application.

If you want to manually download the model:
1. Visit [Hugging Face Hub](https://huggingface.co/Devwa/jackSparrow)
2. Download the `unsloth.Q4_K_M.gguf` file
3. Place it in the appropriate model directory

## Running the Application

1. Make sure your virtual environment is activated
2. Run the chat UI:
```bash
python .venv/Scripts/chat_ui.py
```

## Features

- Modern dark-themed UI
- Real-time conversation with Jack Sparrow's AI
- Message history with timestamps
- Clear chat functionality
- Responsive interface with typing indicators

## Troubleshooting

### Common Issues

1. **Model Loading Error**
   - Ensure you have enough RAM
   - Check that your CPU supports AVX2
   - Verify the model file is correctly downloaded

2. **UI Issues**
   - Make sure tkinter is properly installed
   - Update Python to the latest version
   - Check if your system supports the required fonts

3. **Performance Issues**
   - Adjust the number of CPU threads in `chat_ui.py`
   - Close other resource-intensive applications
   - Consider using a smaller model variant

### Error Messages

If you encounter any of these error messages:
- "Failed to initialize the model": Check your internet connection and model download
- "Module not found": Run the pip install commands again
- "Access denied": Run the terminal as administrator

## Contributing

Feel free to submit issues and enhancement requests!

## License

## Acknowledgments

- LLaMA model by Meta AI
- Pirates of the Caribbean dialogue corpus
- Hugging Face community

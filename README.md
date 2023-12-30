# Audio ChatGPT interface

This is an interface to discuss with ChatGPT in text or audio format.
When you speak, your voice is converted to text and sent to ChatGPT.
When ChatGPT responds, its text is converted to audio and played.

If you write text, then ChatGPT will respond with text.

## Installation

### Configuration of OpenAI API
First, you need to create an account to use the OpenAI API.
Once you have an account, you need to create an API key.

Export the API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```

Top-up your account with some credits to use the API.
One request costs approx. 0.1$ with the current pricing and script configuration.

### Installation

Create a new environment and install the dependencies:

```bash
python -m venv venv
source venv/bin/activate
```

Check that the OpenAI API key is correctly set:

```bash
echo $OPENAI_API_KEY
```
If nothing is printed, then the API key is not set, and you need to set it again.

Once the API key is set, install the dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The script can be run with the following command:

```bash
python main.py
```

The commands are as follows:

| Command         | Description |
-----------------| ---
| r               | starts recording until silence is detected |
| exit            | quits the script |
| {anything else} | sends the text to ChatGPT |


## License
This project is licensed under the terms of the MIT license.

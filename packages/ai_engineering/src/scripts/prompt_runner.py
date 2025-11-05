"""
PromptRunner: A high-level wrapper for running prompt templates against LLMs
and validating their outputs with Guardrails + Pydantic.

Main Features:
--------------
1. Loads configuration (model, temperature, max tokens) from YAML.
2. Renders Jinja templates for prompts.
3. Sends prompts to LLM (via LiteLLM or OpenAI).
4. Validates LLM outputs using a Pydantic schema (BulletinExtraction).
5. Provides both class-based and simple functional interfaces.

Usage Example:
--------------
from src.prompt_runner import run_prompt

result = run_prompt(
    text="Some bulletin text here...",
    template_path="prompts/templates/entity_relation.jinja"
)

print(result)  # Dict validated against BulletinExtraction schema
"""

""" WHY guardrains
We create a gd.Guard object that will check, validate and correct the output of the LLM. This object:

- Enforces the quality criteria specified in the Pydantic RAIL spec.
- Takes corrective action when the quality criteria are not met.
- Compiles the schema and type info from the RAIL spec and adds it to the prompt.
"""
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml
from typing import List, Dict

# LLM imports
try:
    import openai  # Optional: If you want to use OpenAI directly
except ImportError:
    openai = None

from litellm import completion

# Guardrails + Pydantic schema for validation
from guardrails import Guard
# from packages.ai_engineering.src.guardrails_schemas.schemas_guard import BulletinExtraction
from packages.ai_engineering.src.guardrails_schemas.schemas_guard import BulletinExtraction


class PromptRunner:
    """
    Handles prompt rendering, LLM calls, and output validation.

    Attributes
    ----------
    model : str
        Name of the LLM model (default: 'gpt-4o-mini')
    temperature : float
        Sampling temperature for the LLM.
    max_tokens : int
        Maximum tokens in the LLM response.
    env : Environment
        Jinja2 environment for loading templates.
    guard : Guard
        Guardrails instance to validate LLM outputs against BulletinExtraction schema.
    """

    def __init__(self, cfg):
        """
        Initialize PromptRunner by loading configuration and Guardrails.

        Parameters
        ----------
        config_path : str
            Path to the YAML configuration file containing model settings.
        """
        # Initialize Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(searchpath='.'))

        # all providers: https://docs.litellm.ai/docs/providers
        #  mistralAI: https://docs.litellm.ai/docs/providers/mistral
        self.model = cfg.get('model', 'gpt-4o-mini')
        self.temperature = cfg.get('temperature', 0)
        self.max_tokens = cfg.get('max_tokens', 2000)

        # Initialize Guardrails for Pydantic-based validation
        self.guard = Guard.for_pydantic(output_class=BulletinExtraction)

    def render_prompt(self, text: str = None, json_input: dict = None, template_path: str = None) -> str:
        """
        Render a Jinja prompt template with provided text and optional JSON input.

        Parameters
        ----------
        text : str
            The input text to inject into the template.
        json_input : dict
            Optional additional JSON data for the template. e.g. {"date": "1945-05-08", "language": "Dutch"}
        template_path : str
            Path to the Jinja template file.

        Returns
        -------
        str
            The rendered prompt ready to send to the LLM.
        """
        tpl = self.env.get_template(template_path)
        context = {'text': text, 'json_input': json_input}
        return tpl.render(**context)


    def run(self, text: str = None, json_input: dict = None, template_path: str = None) -> dict:
        """
        High-level API to render a prompt, call the LLM, and validate the output.

        Parameters
        ----------
        text : str
            Input text to analyze.
        json_input : dict
            Optional JSON context to pass into the prompt template.
        template_path : str
            Path to the Jinja template file.

        Returns
        -------
        dict
            Validated LLM output.
        """
        prompt = self.render_prompt(text=text, json_input=json_input, template_path=template_path)

        # Call LLM and validate using guard()
        raw_llm_response, validated_response, *rest = self.guard(
            messages=[{"role": "user", "content": prompt}],
            prompt_params={"text": text, **json_input},
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        # validated_response is already a dict matching the Pydantic schema
        return validated_response


    def run_batch(self, items: List[Dict], template_path: str = None) -> list:
        """
        Run inference on a list of dictionaries in batch.

        Parameters
        ----------
        items : list of dict
            A list of input texts and json_inputs.
        template_path : str
            Path to the Jinja template file.

        Returns
        -------
        list
            A list of validated outputs for each input text.
        """
        return [
            self.run(
                text=item["text"],
                json_input=item.get("json_input"),
                template_path=template_path
            )
            for item in items
        ]

# ----------------------------
# Simple helper function for quick one-off calls
# ----------------------------
_runner_instance = None

def run_prompt(text: str, template_path: str, config_path: str = 'configs/settings.yaml') -> dict:
    """
    Convenience function for one-off prompt calls without explicitly creating PromptRunner.

    Parameters
    ----------
    text : str
        Input text for analysis.
    template_path : str
        Path to the Jinja prompt template.
    config_path : str
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Validated LLM output as a Python dictionary.
    """
    global _runner_instance
    if _runner_instance is None:
        _runner_instance = PromptRunner(config_path=config_path)
    return _runner_instance.run(text=text, template_path=template_path)


if __name__ == "__main__":   
    import json 

    runner = PromptRunner()

    items = [
        {"text": "First transcript", "json_input": {"date": "1945-05-08", "language": "Dutch"}},
        {"text": "Second transcript", "json_input": {"date": "1962-10-15", "language": "Dutch"}},
    ]

    prompt = runner.render_prompt(
        text=items[0]['text'], 
        json_input=items[0]['json_input'], 
        template_path='prompts/templates/entity_relation.jinja')
    
    print(prompt)

    data_folder = Path("data/eval")
    data_folder.mkdir(parents=True, exist_ok=True)

    

    # Iterate through all JSON files
    for json_file in data_folder.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(data)
        print(runner.validate_output(data))
    print("✅ Validation complete.")
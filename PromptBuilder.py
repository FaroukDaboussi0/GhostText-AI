import json
from pathlib import Path
from typing import Any, Type
from pydantic import BaseModel

class PromptBuilder:
    """
    Loads a prompt template from disk and builds a prompt by:
      - Filling placeholders with values from an input object (Pydantic instance)
      - Embedding the JSON schema of an output Pydantic model class
    Templates live under a directory, named as <template_name>.<ext>.
    Placeholders use the syntax `${field}` and `${output_class_schema}`.
    """

    def __init__(self, templates_dir: str = "prompt_templates", ext: str = "tpl"):
        self.templates_dir = Path(templates_dir)
        self.ext = ext.lstrip('.')

    def build_prompt(
        self,
        template_name: str,
        input_object: BaseModel,
        output_class: Type[BaseModel]
    ) -> str:
        """
        Build a prompt by loading the template, filling it with input_object values,
        and embedding the JSON schema of output_class.

        :param template_name: Name of the template file (without extension)
        :param input_object: Pydantic model instance whose fields fill placeholders
        :param output_class: Pydantic model class whose schema is injected
        :return: The fully rendered prompt string
        """
        # 1) Load template file
        template_path = self.templates_dir / f"{template_name}.{self.ext}"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        tpl = template_path.read_text(encoding="utf-8")

        # 2) Prepare input substitutions
        # Convert input_object to dict, then each value to string or JSON
        input_values = input_object.model_dump()
        for key, value in input_values.items():
            placeholder = f"${{{key}}}"
            if isinstance(value, (dict, list)):
                filled_value = json.dumps(value)
            else:
                filled_value = str(value)
            tpl = tpl.replace(placeholder, filled_value)

        # 3) Generate JSON schema from output_class
        schema_dict = output_class.schema()
        schema_str = json.dumps(schema_dict, indent=2)
        tpl = tpl.replace("${output_class_schema}", schema_str)

        return tpl
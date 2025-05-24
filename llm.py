import json
import os
import re
import time
from typing import List, Optional, Type, Union
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument, PermissionDenied, ResourceExhausted
from pydantic import BaseModel, ValidationError

load_dotenv(dotenv_path="api_keys.env")

class LLM:
    def __init__(self, model_name: str = "gemini-2.0-flash", max_retries: int = 3):
        print("[INIT] Loading API keys from api_keys.env...")
        self.api_keys = self._load_keys_from_env()
        if not self.api_keys:
            raise RuntimeError("No API keys found in .env file.")

        self.env_path = "api_keys.env"
        self.key_index = 0
        self.max_retries = max_retries
        self.model_name = model_name

        print(f"[INIT] Using model: {model_name}")
        self._configure_api()
        self.model = genai.GenerativeModel(model_name)
        print(f"[INIT] Ready with API key index {self.key_index}")

    def _load_keys_from_env(self) -> List[str]:
        keys = []
        i = 1
        while True:
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if not key:
                break
            keys.append(key)
            print(f"[ENV] Found GOOGLE_API_KEY_{i}")
            i += 1
        print(f"[ENV] Loaded {len(keys)} API keys.")
        return keys

    def _configure_api(self):
        active_key = self.api_keys[self.key_index]
        genai.configure(api_key=active_key)
        print(f"[CONFIG] Configured with API key index {self.key_index}")

    def rotate_key(self):
        old_index = self.key_index
        self.key_index = (self.key_index + 1) % len(self.api_keys)
        self._configure_api()
        print(f"[ROTATE] Switched from key index {old_index} to {self.key_index}")

    def get_active_key(self) -> str:
        return self.api_keys[self.key_index]

    def add_api_key(self, key: str):
        if key not in self.api_keys:
            self.api_keys.append(key)
            print(f"[ADD] Added new API key. Total: {len(self.api_keys)}")
            self._save_api_keys_to_env()
        else:
            print("[ADD] API key already exists.")

    def _save_api_keys_to_env(self):
        print("[SAVE] Persisting API keys to .env file...")
        with open(self.env_path, "r") as f:
            lines = f.readlines()

        existing_keys = {}
        for i, line in enumerate(lines):
            if line.startswith("GOOGLE_API_KEY_"):
                key_num = int(line.split("=")[0].split("_")[-1])
                existing_keys[key_num] = i

        for index, key in enumerate(self.api_keys, start=1):
            line_content = f"GOOGLE_API_KEY_{index}={key}\n"
            if index in existing_keys:
                lines[existing_keys[index]] = line_content
            else:
                lines.append(line_content)

        with open(self.env_path, "w") as f:
            f.writelines(lines)

        print(f"[SAVE] Saved {len(self.api_keys)} API key(s) to .env.")


    def _extract_json_from_response(self,text: str) -> Optional[dict]:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group(1))


    def generate(
        self,
        prompt: Union[str, List[Union[str, Image.Image]]],
        class_output: Type[BaseModel]
    ) -> BaseModel:
        # Ensure the caller passed in a class, not an instance
        if not isinstance(class_output, type) or not issubclass(class_output, BaseModel):
            raise TypeError("`class_output` must be a Pydantic model *class*, not an instance.")

        attempts = 0
        validation_errors = 0

        while True:
            print(f"[GENERATE] Attempt {attempts + 1} using key index {self.key_index}")
            try:
                # 1) Call the LLM
                response = self.model.generate_content(prompt)
                response_text = response.text
                print("[GENERATE] Raw response received.")

                # 2) Extract JSON and instantiate the Pydantic model
                try:
                    json_payload = self._extract_json_from_response(response_text)
                    output_obj = class_output(**json_payload)
                    print("[VALIDATION] Success")
                    return output_obj

                except (json.JSONDecodeError, ValidationError) as ve:
                    validation_errors += 1
                    print(f"[VALIDATION] Failed ({validation_errors}/{self.max_retries}): {ve}")
                    if validation_errors >= self.max_retries:
                        raise RuntimeError("Validation failed too many times.")

            except (InvalidArgument, PermissionDenied, ResourceExhausted) as e:
                attempts += 1
                print(f"[ERROR] LLM API error with key {self.get_active_key()} ({attempts}/{self.max_retries}): {e}")
                if attempts >= self.max_retries:
                    print("[ERROR] All API keys exhausted. Aborting.")
                    raise RuntimeError("All API keys failed. Generation aborted.")
                # Rotate key and retry
                self.rotate_key()
                time.sleep(1)

            except Exception as e:
                validation_errors += 1
                print(f"[ERROR] Unexpected failure ({validation_errors}/{self.max_retries}): {e}")
                if validation_errors >= self.max_retries:
                    raise RuntimeError(f"Unexpected LLM failure: {e}")

            time.sleep(1)
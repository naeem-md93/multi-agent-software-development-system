
import torch
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForCausalLM


class StudentModel:
    def __init__(self, model_name: str = "Qwen/Qwen2-0.5B-Instruct", lr: float = 5e-5):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True).to(self.device)

        # Set pad token if it's not defined
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).to(self.device)
        self.model.config.pad_token_id = self.tokenizer.pad_token_id

        self.optimizer = AdamW(self.model.parameters(), lr=lr)

    def build_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        system_prompt_kwargs: dict = None,
        user_prompt_kwargs: dict = None,
    ) -> str:

        if system_prompt_kwargs is not None:
            system_prompt = system_prompt.format(**system_prompt_kwargs)

        if user_prompt_kwargs is not None:
            user_prompt = user_prompt.format(**user_prompt_kwargs)

        return f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"

    def generate(self, system_prompt: str, user_prompt: str, max_new_tokens: int = 1024) -> str:
        prompt = self.build_prompt(system_prompt, user_prompt)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only the assistant's generated response after the prompt
        return generated_text[len(prompt):].strip()

    def compute_loss(self, system_prompts: list[str], user_prompts: list[str], assistant_responses: list[str]) -> torch.Tensor:

        # Prepare inputs with concatenated full prompt and expected output for causal LM training
        full_prompts = [
            self.build_prompt(sys_p, user_p) + " " + assistant_resp
            for sys_p, user_p, assistant_resp in zip(system_prompts, user_prompts, assistant_responses)
        ]
        tokenized = self.tokenizer(full_prompts, return_tensors="pt", padding=True, truncation=True).to(self.device)
        input_ids = tokenized["input_ids"]

        # Create labels: mask out prompt tokens, only predict assistant response tokens
        labels = input_ids.clone()
        for i, (sys_p, user_p) in enumerate(zip(system_prompts, user_prompts)):
            prompt_len = len(self.tokenizer(self.build_prompt(sys_p, user_p), return_tensors="pt")["input_ids"][0])
            labels[i, :prompt_len] = - 100  # ignore loss on prompt tokens

        outputs = self.model(input_ids, labels=labels)
        return outputs.loss

    def train_on_batch(self, system_prompts, user_prompts, assistant_responses):
        self.model.train()
        loss = self.compute_loss(system_prompts, user_prompts, assistant_responses)
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()
        return loss.item()

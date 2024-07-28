# policypro.py
import streamlit as st
import torch
import torch.nn as nn
from torch.nn import functional as F

def run_policypro():
    # Hyperparameters
    batch_size = 16
    block_size = 32
    max_iters = 5000
    eval_interval = 100
    learning_rate = 1e-3
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    eval_iters = 200
    n_embd = 64
    n_head = 4
    n_layer = 4
    dropout = 0.0

    torch.manual_seed(1337)

    # Load data
    with open('/content/BOBColabProjects/BOBColabProjects/input.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    # Define the model architecture (same as in the training code)
    class BigramLanguageModel(nn.Module):
        def __init__(self, vocab_size, n_embd):
            super().__init__()
            self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
            self.position_embedding_table = nn.Embedding(block_size, n_embd)
            self.blocks = nn.Sequential(*[Block(n_embd, n_head=n_head) for _ in range(n_layer)])
            self.ln_f = nn.LayerNorm(n_embd)
            self.lm_head = nn.Linear(n_embd, vocab_size)

        def forward(self, idx, targets=None):
            B, T = idx.shape
            tok_emb = self.token_embedding_table(idx)
            pos_emb = self.position_embedding_table(torch.arange(T, device=device))
            x = tok_emb + pos_emb
            x = self.blocks(x)
            x = self.ln_f(x)
            logits = self.lm_head(x)

            if targets is None:
                loss = None
            else:
                B, T, C = logits.shape
                logits = logits.view(B*T, C)
                targets = targets.view(B*T)
                loss = F.cross_entropy(logits, targets)

            return logits, loss

        def generate(self, idx, max_new_tokens):
            for _ in range(max_new_tokens):
                idx_cond = idx[:, -block_size:]
                logits, _ = self(idx_cond)
                logits = logits[:, -1, :]
                probs = F.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)
                idx = torch.cat((idx, idx_next), dim=1)
            return idx

    # Define Block class for Transformer block
    class Block(nn.Module):
        def __init__(self, n_embd, n_head):
            super().__init__()
            head_size = n_embd // n_head
            self.sa = MultiHeadAttention(n_head, head_size)
            self.ffwd = FeedForward(n_embd)
            self.ln1 = nn.LayerNorm(n_embd)
            self.ln2 = nn.LayerNorm(n_embd)

        def forward(self, x):
            x = x + self.sa(self.ln1(x))
            x = x + self.ffwd(self.ln2(x))
            return x

    # Define MultiHeadAttention class
    class MultiHeadAttention(nn.Module):
        def __init__(self, num_heads, head_size):
            super().__init__()
            self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
            self.proj = nn.Linear(n_embd, n_embd)
            self.dropout = nn.Dropout(dropout)

        def forward(self, x):
            out = torch.cat([h(x) for h in self.heads], dim=-1)
            out = self.dropout(self.proj(out))
            return out

    # Define Head class for attention head module
    class Head(nn.Module):
        def __init__(self, head_size):
            super().__init__()
            self.key = nn.Linear(n_embd, head_size, bias=False)
            self.query = nn.Linear(n_embd, head_size, bias=False)
            self.value = nn.Linear(n_embd, head_size, bias=False)
            self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
            self.dropout = nn.Dropout(dropout)

        def forward(self, x):
            B, T, C = x.shape
            k = self.key(x)
            q = self.query(x)
            wei = q @ k.transpose(-2, -1) * C**-0.5
            wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
            wei = F.softmax(wei, dim=-1)
            wei = self.dropout(wei)
            v = self.value(x)
            out = wei @ v
            return out

    # Define FeedForward class
    class FeedForward(nn.Module):
        def __init__(self, n_embd):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(n_embd, 4 * n_embd),
                nn.ReLU(),
                nn.Linear(4 * n_embd, n_embd),
                nn.Dropout(dropout),
            )

        def forward(self, x):
            return self.net(x)

    # Load the vocabulary (chars, stoi, itos, encode, decode)
    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    encode = lambda s: [stoi[c] for c in s]  # Encoder: take a string, output a list of integers
    decode = lambda l: ''.join([itos[i] for i in l])  # Decoder: take a list of integers, output a string

    # Load the trained model
    model_path = '/content/BOBColabProjects/BOBColabProjects/bigram_language_model.pth'  # Update with the actual path if different
    model = BigramLanguageModel(vocab_size, n_embd)
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set the model to evaluation mode

    # Streamlit app
    st.title("RBI Guidelines Text Generation")

    # User input for prompt
    prompt = st.text_input("Enter your prompt here:")

    # Number of tokens to generate
    max_new_tokens = st.slider("Number of tokens to generate:", min_value=10, max_value=1000, value=200)

    if st.button("Generate Text"):
        if prompt:
            # Encode the prompt
            encoded_prompt = torch.tensor(encode(prompt), dtype=torch.long).unsqueeze(0)

            # Generate text
            generated_sequence = model.generate(encoded_prompt, max_new_tokens=max_new_tokens)
            decoded_sequence = decode(generated_sequence[0].tolist())

            # Caesar cipher decoding
            key = 3
            decoded_output = ""
            for char in decoded_sequence[len(prompt):]:  # Start decoding after the prompt
                if char.isalpha():
                    start = ord('a') if char.islower() else ord('A')
                    shifted_char = chr((ord(char) - start - key) % 26 + start)
                else:
                    shifted_char = char
                decoded_output += shifted_char

            # Display decoded output
            st.subheader("Generated Text:")
            st.write(decoded_output)
        else:
            st.warning("Please enter a prompt.")

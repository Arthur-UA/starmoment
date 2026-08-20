# StarMoment

Turn a personal memory and NASA's Astronomy Picture of the Day into a short,
streaming celestial keepsake.

## Run locally

Install deps with:
```bash
uv sync
```

Create a `.env` file containing your OpenAI API key (No need to do this if you use vLLM self-hosted model):

```env
OPENAI_API_KEY=your-key-here
```

Then start the site:

```bash
uv run main.py
```

Open <http://127.0.0.1:8000> in your browser.

## Start the vLLM local LLM serving

These models should be able to fit in 6GB vRAM:
- ```Qwen/Qwen3.5-0.8B```
- ```LiquidAI/LFM2.5-VL-1.6B```

```bash
export VLLM_USE_FLASHINFER_SAMPLER=0
vllm serve Qwen/Qwen3.5-0.8B \
  --max-model-len 2048 \
  --max-num-seqs 1
```

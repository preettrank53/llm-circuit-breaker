# Contributing to LLM Budget Guard

First off, thank you for considering contributing to LLM Budget Guard! It's people like you that make this tool safe, reliable, and useful for the community.

## Local Development Setup

To get your development environment set up, please follow these exact steps:

1. **Fork and Clone the Repository**
   Fork the repository on GitHub, then clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/llm-circuit-breaker.git
   cd llm-circuit-breaker
   ```

2. **Create a Virtual Environment**
   It is highly recommended to isolate your dependencies:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies in Editable Mode**
   Install the package itself, plus the required testing libraries:
   ```bash
   pip install -e .
   pip install pytest httpx
   ```

4. **Run the Test Suite**
   We enforce a strict testing policy. Before submitting any Pull Request, ensure the entire test suite passes:
   ```bash
   pytest tests/ -v
   ```
   *Note: Our tests use a mock database and mock HTTP requests. They do not require an active OpenAI API key or internet connection.*

## Submitting a Pull Request

1. Create a new branch for your feature or bugfix (`git checkout -b feature/your-feature-name`).
2. Make your changes and write tests if applicable.
3. Ensure all tests pass (`pytest tests/`).
4. Commit your changes with a clear, descriptive commit message.
5. Push to your fork and submit a Pull Request against the `main` branch.

If you are looking for a place to start, check out the issues labeled `good first issue` in the GitHub tracker!

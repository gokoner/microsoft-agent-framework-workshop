# Contributing to Microsoft Agent Framework Workshop

Thank you for your interest in contributing to this workshop! This guide will help you get started.

## How to Contribute

We welcome contributions in the following areas:

- **New Tutorials**: Add new workshop modules covering additional topics
- **Improvements**: Enhance existing tutorials with better examples or explanations
- **Bug Fixes**: Fix errors or issues in notebooks or code
- **Documentation**: Improve README, setup instructions, or tutorial documentation
- **Sample Data**: Contribute real-world examples and datasets

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Azure subscription (for Azure AI Foundry tutorials)
- OpenAI API key or Azure OpenAI endpoint
- Git and GitHub account

### Setup Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/microsoft-agent-framework-workshop.git
   cd microsoft-agent-framework-workshop
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (recommended for contributors)
   pip install -r requirements-dev.txt
   ```

5. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

6. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and endpoints
   ```

7. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Alternative: Docker Development Environment

For a consistent, isolated development environment:

```bash
# Start the workshop environment
docker-compose up

# Access JupyterLab at http://localhost:8888
# Your changes will be reflected immediately due to volume mounting
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use clear, descriptive variable and function names
- Add comments for complex logic
- Keep code examples simple and focused on learning
- Use `black` for code formatting (line length: 100)
- Use `isort` for import sorting
- Run `pre-commit run --all-files` before committing (if pre-commit hooks installed)

**Automated Formatting:**
```bash
# Format Python code
black .

# Sort imports
isort .

# Check with flake8
flake8 .
```

### Jupyter Notebooks

- **Structure**: Follow the existing tutorial structure with clear sections
- **Headers**: Use markdown headers to organize content logically
- **Explanations**: Include detailed explanations before code cells
- **Output**: Clear output cells with meaningful examples
- **Time Estimates**: Update duration estimates in README if adding new content

### Documentation

- Update README.md if adding new tutorials
- Include learning objectives and prerequisites
- Provide clear setup instructions
- Add troubleshooting tips for common issues

### Commit Messages

Write clear, descriptive commit messages:

```
Add tutorial on custom tool integration

- Create new notebook 15_custom_tools.ipynb
- Add examples for HTTP API and database tools
- Update README with new tutorial entry
```

## Tutorial Contribution Checklist

When adding a new tutorial, ensure:

- [ ] Tutorial follows the progressive learning structure
- [ ] Code examples are tested and working
- [ ] Clear learning objectives stated at the beginning
- [ ] Environment setup instructions included
- [ ] Time estimate provided
- [ ] README.md updated with tutorial entry
- [ ] Sample data included if needed
- [ ] Key concepts explained before implementation
- [ ] Best practices and production tips included
- [ ] Quick reference section at the end

## Submitting Changes

1. **Test your changes**:
   - Run all notebook cells to ensure they execute without errors
   - Verify output is as expected
   - Test with fresh environment if possible

2. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of changes
   - Link any related issues

### Pull Request Guidelines

- **Title**: Clear and descriptive (e.g., "Add tutorial on API integration patterns")
- **Description**: Explain what changes you made and why
- **Testing**: Describe how you tested your changes
- **Screenshots**: Include screenshots for UI changes or new visualizations
- **Breaking Changes**: Clearly document any breaking changes

## Code Review Process

1. Maintainers will review your pull request
2. Address any feedback or requested changes
3. Once approved, your contribution will be merged
4. Your changes will be included in the next release

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the problem
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, relevant package versions
- **Screenshots**: If applicable
- **Error Messages**: Full error messages and stack traces

### Feature Requests

When requesting features:

- **Use Case**: Describe the problem you're trying to solve
- **Proposed Solution**: Your idea for how to address it
- **Alternatives**: Other solutions you've considered
- **Learning Value**: How it benefits workshop participants

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

## Questions?

- **Issues**: Open an issue for questions or discussions
- **Documentation**: Check existing tutorials and README first
- **Azure Resources**: Refer to [Azure AI documentation](https://learn.microsoft.com/en-us/azure/ai-services/agents/)

## Recognition

Contributors will be:
- Listed in project documentation
- Credited in release notes
- Acknowledged in the community

Thank you for helping make this workshop better for everyone! 🎉

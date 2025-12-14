# AI-Powered Programming Crew

Autonomous software development team powered by CrewAI that transforms requirements into production-ready applications.

## Overview

This CrewAI application simulates a complete software development team with specialized AI agents working together to build applications from scratch. The system follows industry best practices with a full SDLC workflow: business analysis, architecture design, implementation, testing, code review, and documentation.

## Features

- **Business Analysis**: Transforms requirements into detailed specifications with user stories and data models
- **Architecture Design**: Creates modular architecture with clean separation of concerns
- **Backend Development**: Implements domain-driven design with proper validation and error handling
- **Testing**: Generates comprehensive test suites with unit, integration, and edge case coverage
- **Code Review**: Automated quality assessment with security, performance, and best practices analysis
- **Documentation**: Creates professional README files with usage examples and API references

## Architecture

### AI Agents

- **Business Analyst**: Analyzes requirements and creates structured business specifications
- **Engineering Lead**: Designs module breakdown and system architecture
- **Backend Architect**: Defines database schemas, API structure, and data access patterns
- **Backend Developer**: Implements business logic following SOLID principles
- **Frontend Engineer**: Creates Gradio-based user interfaces
- **Test Planner**: Designs comprehensive test strategies
- **Test Engineer**: Implements pytest test suites
- **Code Reviewer**: Reviews code quality, security, and performance
- **Documentation Writer**: Creates user-facing documentation

### Workflow

```
Requirements → Business Analysis → Architecture Design → Implementation →
Testing → Code Review → Documentation → Production Code
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file based on `.env_example`:

```bash
cp .env_example .env
```

Required environment variables:

- `OPENAI_API_KEY`: OpenAI API key for LLM access
- `OPENAI_MODEL_NAME`: Model to use (default: gpt-4)
- `MOONSHOT_API_KEY`: Alternative API key (optional)
- `MOONSHOT_BASE_URL`: Alternative API base URL (optional)

## Usage

### Basic Usage

```python
from my_programming_crew.crew import MyProgrammingCrew

requirements = """
Create a trading simulation account management system where users can:
- Create accounts and manage funds
- Deposit and withdraw money
- Buy and sell shares
- Track portfolio value and profit/loss
"""

crew = MyProgrammingCrew()
result = crew.crew().kickoff(inputs={'requirements': requirements})
```

### Running from Command Line

```bash
crewai run
```

## Project Structure

```
my_programming_crew/
├── src/
│   └── my_programming_crew/
│       ├── config/
│       │   ├── agents.yaml      # Agent definitions
│       │   └── tasks.yaml       # Task definitions
│       ├── crew.py              # Main crew orchestration
│       ├── main.py              # Entry point
│       └── tools/               # Custom tools
├── output/                      # Generated application code
├── tests/                       # Test files
├── .env                        # Environment variables (not in git)
├── .env_example                # Environment template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Output Structure

Generated applications are placed in the `output/` directory with the following structure:

```
output/
├── *.py                        # Implementation modules
├── test_*.py                   # Test files
├── demo_app.py                 # Demo application
├── main_app.py                 # Frontend application
├── README.md                   # Application documentation
└── json/                       # Intermediate outputs
    ├── 01_business_requirements.json
    ├── 02_module_breakdown.json
    ├── 03_backend_architecture.json
    └── ...
```

## Development Workflow

The crew follows this development process:

1. **Business Analysis** (Phase 0)
   - Analyzes requirements
   - Creates user stories
   - Defines data models
   - Identifies business rules

2. **Architecture** (Phase 1)
   - Module breakdown
   - Class design
   - Dependency management
   - Backend architecture

3. **Implementation** (Phase 2)
   - Dynamic task creation per module
   - Backend implementation
   - Frontend development

4. **Testing** (Phase 3)
   - Test planning
   - Test implementation
   - Coverage analysis

5. **Quality Assurance** (Phase 4)
   - Code review
   - Security analysis
   - Performance optimization

6. **Documentation** (Phase 5)
   - README generation
   - API documentation
   - Usage examples

## Example Output

The crew has successfully generated:

- **Trading Simulation Platform**: Complete account management system with deposits, withdrawals, and transaction tracking
- **28 Test Cases**: 100% passing rate with comprehensive coverage
- **6 Modules**: Clean architecture with proper separation of concerns
- **Full Documentation**: Professional README with examples and API reference

## Technology Stack

- **Framework**: CrewAI
- **LLM**: OpenAI GPT-4 / Moonshot AI
- **Language**: Python 3.9+
- **Testing**: pytest
- **Frontend**: Gradio (generated)
- **Data**: Pydantic models

## Business Rules Enforcement

Generated applications include:

- Input validation with custom exceptions
- Business rule validation (min/max amounts, balance checks)
- Immutable transaction records
- Decimal precision for financial calculations
- Comprehensive error handling

## Testing

```bash
pytest output/test_*.py -v
```

Example test output:
```
28 passed in 0.11s
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

Built with CrewAI - AI agent orchestration framework

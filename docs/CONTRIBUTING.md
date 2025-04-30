# Contributing to CareHub

Thank you for your interest in contributing to **CareHub**, the Beauty & Wellness Booking Platform! We welcome contributions from the community to enhance our platform and make booking services seamless for everyone. This guide outlines how to contribute effectively, whether you're fixing bugs, adding features, improving documentation, or suggesting ideas.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Setting Up the Development Environment](#setting-up-the-development-environment)
- [Development Guidelines](#development-guidelines)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Bugs and Suggesting Features](#reporting-bugs-and-suggesting-features)
- [Contact](#contact)

---

## Code of Conduct

We are committed to fostering an inclusive and respectful community. All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it to understand the behavior we expect and how to report issues.

---

## How Can I Contribute?

There are many ways to contribute to CareHub, including:

- **Code Contributions**: Fix bugs, implement features, or optimize performance.
- **Documentation**: Improve README, wiki, or add guides in the `docs/` directory.
- **Bug Reports**: Identify and report issues via GitHub Issues.
- **Feature Suggestions**: Propose new ideas to enhance the platform.
- **Testing**: Write or improve unit and integration tests.
- **Design**: Contribute to UI/UX improvements using Tailwind CSS or JavaScript.

No contribution is too small! Whether you're a beginner or an experienced developer, we value your input.

---

## Setting Up the Development Environment

To contribute code or documentation, set up the CareHub project locally by following these steps:

1. **Fork the Repository**:
   - Click the "Fork" button on the [CareHub GitHub repository](https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio).
   - Clone your fork:
     ```bash
     git clone https://github.com/<your-username>/quantum-trio.git
     cd quantum-trio
     ```

2. **Set Up the Environment**:
   - Follow the detailed setup instructions in [docs/setup.md](docs/setup.md) to:
     - Install Python, PostgreSQL, and other prerequisites.
     - Create a virtual environment and install dependencies (`pip install -r requirements.txt`).
     - Configure the PostgreSQL database and `.env` file.
     - Run migrations (`python manage.py migrate`).
     - Start the development server (`python manage.py runserver`).

3. **Verify Setup**:
   - Access the app at `http://127.0.0.1:8000/`.
   - Ensure you can log in and test core features (e.g., search, booking).

---

## Development Guidelines

To maintain code quality and consistency, follow these guidelines:

### Branch Naming
- Create a new branch for each contribution.
- Use descriptive branch names based on the type of work:
  - `feature/<feature-name>` (e.g., `feature/add-multi-language-support`)
  - `bugfix/<issue-number>` (e.g., `bugfix/123-login-error`)
  - `docs/<doc-name>` (e.g., `docs/update-readme`)
- Keep branch names lowercase and use hyphens (`-`) for spaces.

### Coding Standards
- **Python/Django**:
  - Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
  - Use Django’s best practices (e.g., DRY, modular views).
  - Add docstrings for functions and classes.
- **Frontend**:
  - Use Tailwind CSS classes for styling, following the existing structure.
  - Write clean, modular JavaScript (ES6+).
  - Ensure responsiveness across devices.
- **Database**:
  - Update the ER diagram (`CareHUB.drawio.png`) if schema changes are made.
  - Use migrations for database changes (`python manage.py makemigrations`).
- **Testing**:
  - Write unit and integration tests for new features or bug fixes.
  - Run tests with `python manage.py test` before submitting.
- **Security**:
  - Follow OWASP guidelines for secure coding (e.g., sanitize inputs, use Django’s CSRF protection).

### Commit Messages
- Write clear, concise commit messages in the imperative mood.
- Include the issue number if applicable (e.g., `#123`).
- Examples:
  - `Add user authentication for shop accounts (#45)`
  - `Fix broken search filter for location`
  - `Update setup.md with Node.js instructions`
- Keep commits small and focused on a single change.

### Code Quality
- Ensure code passes SonarCloud checks (bugs, vulnerabilities, code smells).
- Run linters (e.g., `flake8` for Python) and formatters (e.g., `prettier` for JavaScript) if configured.
- Test locally to confirm your changes don’t break existing functionality.

---

## Submitting a Pull Request

1. **Create a Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**:
   - Implement your feature, fix, or documentation update.
   - Test thoroughly (run `python manage.py test` and check the app locally).

3. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message (#issue-number)"
   ```

4. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**:
   - Go to the [CareHub repository](https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio).
   - Click “New Pull Request” and select your branch.
   - Fill out the PR template (if available) with:
     - Description of changes.
     - Related issue number (e.g., “Closes #123”).
     - Screenshots or steps to test (if applicable).
   - Submit the PR and wait for review.

6. **Address Feedback**:
   - Respond to reviewer comments and make requested changes.
   - Push updates to the same branch; they’ll automatically appear in the PR.

**Note**: Pull requests must pass code review and automated checks (e.g., SonarCloud) before merging. Ensure your code adheres to the [Development Guidelines](#development-guidelines).

---

## Reporting Bugs and Suggesting Features

### Reporting Bugs
- Check the [GitHub Issues](https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio/issues) to avoid duplicates.
- Open a new issue with:
  - **Title**: Clear summary (e.g., “Login fails with invalid credentials”).
  - **Description**: Steps to reproduce, expected behavior, actual behavior, and screenshots if possible.
  - **Environment**: Browser, OS, and app version (if known).
  - **Labels**: Add `bug` and other relevant labels.

### Suggesting Features
- Open a new issue with the `enhancement` label.
- Include:
  - **Title**: Feature summary (e.g., “Add multi-language support”).
  - **Description**: Problem it solves, proposed solution, and potential impact.
  - **Use Case**: Example of how it benefits users or shops.
- Discuss the idea with the team before starting work.

---

## Contact

For questions or clarification, reach out to the Quantum Trio team:

- **GitHub Issues**: [Create an issue](https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio/issues)
- **Email**: [quantum.trio@example.com](mailto:quantum.trio@example.com)
- **Wiki**: Check the [Project Wiki](https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio/wiki) for additional resources.

---

## Acknowledgments

Thank you for contributing to CareHub! Your efforts help make beauty and wellness bookings more accessible and efficient for everyone. We look forward to collaborating with you!

<p align="center">
  Built with ❤️ by <a href="https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio">Quantum Trio</a>
</p>

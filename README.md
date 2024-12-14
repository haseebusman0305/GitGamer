# GitGamer 🎮

Create customized commit histories in your Git repository with random but realistic-looking commit patterns! Perfect for testing repositories or creating artistic contribution graphs.

## ⚠️ Disclaimer

This tool is for educational and testing purposes only. We encourage authentic contributions and meaningful code development. The true value of a developer lies in their actual work, not in activity metrics.

## ✨ Features

- Customize total number of commits
- Set maximum commits per day
- Define maximum gap between commit dates
- Control how far back in time commits can go
- Realistic commit messages
- Supports remote repository integration
- Respects .gitignore patterns
- Works with existing repositories
- Randomized commit times during working hours
- Maintains Git author configuration

## 🔧 Installation

1. Ensure you have Python 3.x and Git installed
2. Clone this repository:
   ```bash
   git clone https://github.com/haseebusman0305/GitGamer.git
   cd GitGamer
   ```
3. Install the required dependency:
   ```bash
   pip install pathspec
   ```

## 🚀 Usage

1. Run the script:
   ```bash
   python main.py
   ```

2. Follow the prompts to configure:
   - Total number of commits desired
   - Target folder path
   - Maximum commits per day (default: 5)
   - Maximum gap between commits in days (default: 2)
   - Maximum days to go back in history (default: 30)
   - Remote repository URL (optional)
   - Git author name and email (defaults to your git config)

## 📝 Example Configuration

```plaintext
=== GitGamer Configuration ===
Enter total number of commits you want: 100
Enter the folder path: /path/to/your/repo
Enter maximum commits per day (default 5): 5
Enter maximum gap between commits in days (default 2): 2
Enter maximum days in past (default 30): 30
Enter remote repository URL (optional, press Enter to skip): https://github.com/username/repo.git

=== Git Author Configuration ===
Enter your Git name (default from git config): John Doe
Enter your Git email (default from git config): john@example.com
```

## 🎯 How It Works

- Creates commits with random but realistic timestamps
- Distributes commits across the specified date range
- Respects maximum commits per day limit
- Adds small modifications to existing files
- Uses varied, realistic-looking commit messages
- Maintains consistent author information
- Properly handles timezone information
- Respects .gitignore patterns

## ⚠️ Important Notes

- Use this tool responsibly and ethically
- Not recommended for production repositories
- Make sure to backup your repository before using
- Verify your Git configuration before running
- May need appropriate permissions for remote pushes

## 📄 License

This project is open-sourced under the MIT License. See the LICENSE file for details.

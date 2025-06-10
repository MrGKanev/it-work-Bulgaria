# Bulgarian IT Job Tracker

Автоматичен scraper за следене на броя IT обяви в България по сайтове и локации.

## Функционалности

- 📊 Ежедневно събиране на брой обяви от dev.bg и jobs.bg
- 📍 Проследяване по категории: Общо, Русе, Remote работа  
- 📅 Съхранение в CSV файлове по месеци и години
- 🔄 Автоматично commit и push в GitHub
- 🛠 Модулна архитектура за лесно добавяне на нови сайтове

## Структура на проекта

```
job-tracker/
├── data/
│   └── 2025/
│       └── June-2025.csv
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py      # Базов клас за scrapers
│   ├── dev_bg_scraper.py    # dev.bg scraper
│   └── jobs_bg_scraper.py   # jobs.bg scraper
├── config/
│   ├── sites.json           # Конфигурация на сайтовете
│   └── settings.py          # Общи настройки
├── main.py                  # Главен скрипт
├── utils.py                 # Помощни функции
├── requirements.txt
└── README.md
```

## Инсталация

1. **Клониране на repository:**

```bash
git clone <your-repo-url>
cd job-tracker
```

2. **Инсталиране на dependencies:**

```bash
pip install -r requirements.txt
```

3. **Настройване на Git (ако е нужно):**

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Използване

### Еднократно изпълнение

```bash
python main.py
```

### Автоматизация с cron (Linux/Mac)

```bash
# Редактиране на crontab
crontab -e

# Добавяне на ред за ежедневно изпълнение в 9:00 сутринта
0 9 * * * cd /path/to/job-tracker && python main.py
```

## CSV Формат

Данните се записват в следния формат:

| Date       | Site   | Total_Jobs | Ruse_Jobs | Remote_Jobs | Notes          |
|------------|--------|------------|-----------|-------------|----------------|
| 2025-06-10 | dev.bg | 150        | 12        | 45          | Daily scraping |
| 2025-06-10 | jobs.bg| 320        | 28        | 89          | Daily scraping |

## Добавяне на нови сайтове

1. **Създайте нов scraper файл** в `scrapers/`:

```python
# scrapers/new_site_scraper.py
from .base_scraper import BaseScraper

class NewSiteScraper(BaseScraper):
    def __init__(self, config):
        super().__init__("new-site", config)
    
    def scrape(self):
        results = self.scrape_all_categories()
        return {
            'total': results.get('total'),
            'ruse': results.get('ruse'),
            'remote': results.get('remote')
        }
```

2. **Добавете конфигурация** в `config/sites.json`:

```json
{
  "new-site": {
    "urls": {
      "total": "https://new-site.com/jobs",
      "ruse": "https://new-site.com/jobs?location=ruse",
      "remote": "https://new-site.com/jobs?remote=true"
    },
    "selectors": {
      "job_count": [".jobs-count", ".results-number"],
      "fallback_patterns": ["(\\d+) обяви"]
    }
  }
}
```

3. **Обновете main.py** за да включи новия scraper:

```python
scrapers = {
    'dev.bg': DevBgScraper,
    'jobs.bg': JobsBgScraper,
    'new-site': NewSiteScraper  # Добавете тук
}
```

## Логове

Логовете се записват в:

- Console output
- `job_tracker.log` файл

Ниво на логване се контролира от `LOG_LEVEL` в `config/settings.py`.

## Настройки

Основните настройки са в `config/settings.py`:

- `REQUEST_TIMEOUT`: Timeout за HTTP заявки
- `REQUEST_RETRIES`: Брой опити при неуспех
- `USER_AGENT`: User agent за заявките
- `LOG_LEVEL`: Ниво на логване

## Troubleshooting

### Грешки при scraping

1. Проверете дали сайтът е достъпен
2. Проверете селекторите в `config/sites.json`
3. Проверете логовете за детайли

### Git грешки

1. Уверете се че имате права за push в repository
2. Проверете Git конфигурацията
3. Проверете че сте в правилната директория

### CSV грешки

1. Проверете че `data/` директорията съществува
2. Проверете правата за писане

## Структура на данните

Файловете се организират по следния начин:

```
data/
├── 2025/
│   ├── January-2025.csv
│   ├── February-2025.csv
│   ├── ...
│   └── December-2025.csv
└── 2026/
    ├── January-2026.csv
    └── ...
```

from bs4 import BeautifulSoup
from urllib.parse import urlencode
import json
import requests


def fetch_article_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        headline_tag = soup.find("h3", class_="gnw_heading")
        headline = headline_tag.get_text(strip=True) if headline_tag else "No headline found"

        paragraphs = soup.find_all("p")
        article_content = "\n".join(paragraph.get_text(strip=True) for paragraph in paragraphs)

        return {"headline": headline, "content": article_content}
    else:
        return {"error": f"Failed to fetch the article. Status code: {response.status_code}"}


def fetch_news_for_company(company_name, gcfIssuerId):
    base_url = "https://api.news.eu.nasdaq.com/news/query.action"

    query_params = {
        "callback": "companyNews.callback",
        "type": "json",
        "globalGroup": "exchangeNotice",
        "globalName": "MicrositeFilter",
        "showAttachments": "true",
        "showCnsSpecific": "true",
        "showCompany": "true",
        "displayLanguage": "en",
        "dateMask": "yyyy-MM-dd HH:mm:ss",
        "timeZone": "CET",
        "gcfIssuerId": gcfIssuerId,
    }

    try:
        full_url = base_url + "?" + urlencode(query_params)
        response = requests.get(full_url)
        response.raise_for_status()
        if response.status_code == 200:
            json_data = response.text.lstrip(query_params["callback"] + "(").rstrip(");")
            data = json.loads(json_data)
            if "results" in data and "item" in data["results"]:
                news_data = []
                for item in data["results"]["item"][:3]:  # Limit to 3 most recent articles
                    title = item.get("headline", "No title found")
                    message_url = item.get("messageUrl", "No URL found")
                    publication_date = item.get("published", "No publication date found")
                    article_content = fetch_article_content(message_url)
                    if "error" in article_content:
                        print(article_content["error"])
                    else:
                        news_data.append(
                            {
                                "Company": company_name,
                                "title": title,
                                "Message URL": message_url,
                                "Content": article_content["content"],
                                "date": publication_date,
                            }
                        )
                return news_data
            else:
                print(f"No news items found for {company_name}")
                return []
        else:
            print(f"Failed to fetch data for {company_name}. Status code: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"RequestException: Error fetching data for {company_name}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: Error decoding JSON for {company_name}: {e}")
        return []
    except Exception as e:
        print(f"Exception: Error fetching data for {company_name}: {e}")
        return []
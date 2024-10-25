import requests
from bs4 import BeautifulSoup
import csv
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')
    

def extract_information(job):
    job_title = job.find('div', class_='sc-f5007364-4').text.strip()
    workplace = job.find('div', class_='sc-f5007364-5').text.strip()
    employment_type = job.find('div', class_='sc-f5007364-6').text.strip()

    return job_title, workplace, employment_type

def extract_jobs_paginated(base_url, csv_file):
    page = 1


    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Cargo', 'Localidade', 'Efetividade'])

        while True:
            url = f"{base_url}?page={page}"
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_list = soup.find('ul', {'data-testid': 'job-list__list'})

                if job_list:
                    jobs = job_list.find_all('li', {'data-testid': 'job-list__listitem'})
                    for job in jobs:
                        information = extract_information(job)
                        writer.writerow(information)

                    next_page_link = soup.find('a', {'aria-label': 'Next Page'})
                    if not next_page_link:
                        break  

                    page += 1
                else:
                    print(f"Informações não encontradas na página {url}")
                    break  

            else:
                print(f"Erro ao acessar a página {url}. Status code: {response.status_code}")
                break

@app.route('/')
def show_jobs():
    csv_file = 'jobs.csv'
    extract_jobs_paginated('https://gruposeb.gupy.io', csv_file)
    
    jobs = []
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            jobs.append(row)

    return render_template('dados.html', dados=jobs)

if __name__ == "__main__":
    app.run(debug=True)

import json
import os
import requests
from datetime import datetime
from pyquery import PyQuery
import boto3

FUCK_HABR_URL = (
    "https://freelance.habr.com/tasks?"
    "categories="
    "development_all_inclusive%2"
    "Cdevelopment_backend%2Cdevelopment_frontend%2Cdevelopment_prototyping%2C"
    "development_ios%2Cdevelopment_android%2Cdevelopment_desktop%2Cdevelopment_bots%2Cdevelopment_games%2"
    "Cdevelopment_1c_dev%2Cdevelopment_scripts%2Cdevelopment_voice_interfaces%2Cdevelopment_other%2C"
    "testing_sites%2Ctesting_mobile%2Ctesting_software%2Cadmin_servers%2Cadmin_network%2C"
    "admin_databases%2Cadmin_security%2Cadmin_other%2Cdesign_sites%2Cdesign_landings%2Cdesign_logos%2C"
    "design_illustrations%2Cdesign_mobile%2Cdesign_icons%2Cdesign_polygraphy%2Cdesign_banners%2C"
    "design_graphics%2Cdesign_corporate_identity%2Cdesign_presentations%2Cdesign_modeling%2C"
    "design_animation%2Cdesign_photo%2Cdesign_other%2Ccontent_copywriting%2Ccontent_rewriting%2C"
    "content_audio%2Ccontent_article%2Ccontent_scenarios%2Ccontent_naming%2Ccontent_correction%2C"
    "content_translations%2Ccontent_coursework%2Ccontent_specification%2Ccontent_management%2C"
    "content_other%2Cmarketing_smm%2Cmarketing_seo%2Cmarketing_context%2Cmarketing_email%2C"
    "marketing_research%2Cmarketing_sales%2Cmarketing_pr%2Cmarketing_other%2Cother_audit_analytics%2C"
    "other_consulting%2Cother_jurisprudence%2Cother_accounting%2Cother_audio%2Cother_video%2Cother_engineering%2Cother_other"
    '&page='
)

def handler(event, context):
    going = True
    page = 1
    ids_list = []

    while going:
        req = requests.get(FUCK_HABR_URL + str(page))
        print('GET: ' + FUCK_HABR_URL + str(page))
        query = PyQuery(req.text)
        links = query('#tasks_list > .content-list__item .task__title a')

        for item in links:
            href = PyQuery(item).attr('href')
            id = href.split('/')[2]
            ids_list.append(id)

        if (len(links) == 0):
            going = False
        page = page + 1

    orders_list = []

    for id in ids_list:
        req = requests.get('https://freelance.habr.com/tasks/' + id)
        print('GET: ' + 'https://freelance.habr.com/tasks/' + id)

        query = PyQuery(req.text)

        title = query('body > div.layout > main > section > div > div > div > div.task.task_detail > h2').text().replace('\n', ' ')
        description = query('.task__description').html()

        tags = []
        for tag_q in query('.tags__item_link'):
            tags.append(PyQuery(tag_q).text())

        meta = query('.task__meta').text().split('•')
        print(meta)
        clicks = int(meta[1].split(' ')[1])
        views = int(meta[2].split(' ')[1])

        order_obj = {
            'habrId': int(id),
            'title': title,
            'description': description,
            'tags': tags,
            'clicks': clicks,
            'views': views,
        }

        orders_list.append(order_obj)

    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url=os.environ['ENDPOINT_URL']
    )

    s3.put_object(Bucket=os.environ['BUCKET_NAME'], Key=str(datetime.now()) + '.json', Body=json.dumps(orders_list))

    return {
        'statusCode': 200,
    }

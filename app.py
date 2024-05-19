from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import json
from statistics import mean
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на ваш секретный ключ


def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


subscribers = load_data('subscribers.json')
postmen = load_data('postmen.json')
publications = load_data('publications.json')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', subscribers=subscribers, postmen=postmen, publications=publications)


@app.route('/add_info', methods=['GET'])
def add_info():
    if 'username' in session and session['username'] == 'admin':
        return render_template('add_info.html')
    else:
        flash('Пожалуйста, войдите для доступа к админ-панели.')
        return redirect(url_for('login'))


@app.route('/add_subscriber', methods=['POST'])
def add_subscriber():
    if 'username' in session and session['username'] == 'admin':
        name = request.form.get('name')
        address = request.form.get('address')
        publications_list = request.form.get('publications').split(',')
        delivery_start = request.form.get('delivery_start')
        subscription_duration = int(request.form.get('subscription_duration'))

        new_subscriber = {
            "name": name,
            "address": address,
            "publications": publications_list,
            "delivery_start": delivery_start,
            "subscription_duration": subscription_duration
        }
        subscribers.append(new_subscriber)

        save_data(subscribers, 'subscribers.json')

        return redirect(url_for('add_info'))
    else:
        flash('Недостаточно прав.')
        return redirect(url_for('login'))


@app.route('/add_postman', methods=['POST'])
def add_postman():
    if 'username' in session and session['username'] == 'admin':
        name = request.form.get('name')
        section = request.form.get('section')
        addresses = request.form.get('addresses').split(',')

        new_postman = {"name": name, "section": section, "addresses": addresses}
        postmen.append(new_postman)

        save_data(postmen, 'postmen.json')

        return redirect(url_for('add_info'))
    else:
        flash('Недостаточно прав.')
        return redirect(url_for('login'))


@app.route('/add_publication', methods=['POST'])
def add_publication():
    if 'username' in session and session['username'] == 'admin':
        name = request.form.get('name')
        index = request.form.get('index')
        price = float(request.form.get('price'))

        new_publication = {"name": name, "index": index, "price": price}
        publications.append(new_publication)

        save_data(publications, 'publications.json')

        return redirect(url_for('add_info'))
    else:
        flash('Недостаточно прав.')
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('add_info'))
        else:
            flash('Неправильное имя пользователя или пароль.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/postman_by_address', methods=['GET'])
def postman_by_address():
    address = request.args.get('address')
    for postman in postmen:
        if address in postman['addresses']:
            return render_template('index.html', subscribers=subscribers, postmen=postmen, publications=publications,
                                   postman_name=postman['name'])
    return render_template('index.html', subscribers=subscribers, postmen=postmen, publications=publications,
                           postman_name=None)


@app.route('/subscribers_by_section', methods=['GET'])
def subscribers_by_section():
    section = request.args.get('section')
    subscribers_in_section = [subscriber for subscriber in subscribers if any(
        address in subscriber['address'] for address in
        [postman['addresses'] for postman in postmen if postman['section'] == section][0])]
    return render_template('index.html', subscribers=subscribers_in_section, postmen=postmen, publications=publications,
                           section=section)


@app.route('/postman_count', methods=['GET'])
def postman_count():
    count = len(postmen)
    return render_template('index.html', subscribers=subscribers, postmen=postmen, publications=publications,
                           postman_count=count)


@app.route('/section_with_max_publications', methods=['GET'])
def section_with_max_publications():
    section_publication_count = {postman['section']: 0 for postman in postmen}
    for subscriber in subscribers:
        for postman in postmen:
            if subscriber['address'] in postman['addresses']:
                section_publication_count[postman['section']] += len(subscriber['publications'])
                break
    max_section = max(section_publication_count, key=section_publication_count.get)
    return render_template('section_with_max_publications.html', section=max_section, count=section_publication_count[max_section])

@app.route('/average_subscription_duration', methods=['GET'])
def average_subscription_duration():
    publication_durations = {pub['name']: [] for pub in publications}
    for subscriber in subscribers:
        for publication in subscriber['publications']:
            publication_durations[publication].append(subscriber['subscription_duration'])
    average_durations = {pub: mean(durations) for pub, durations in publication_durations.items()}
    return render_template('average_subscription_duration.html', average_durations=average_durations)



if __name__ == '__main__':
    app.run(debug=True)

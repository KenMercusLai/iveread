import datetime
import json
from collections import defaultdict

import plotly
import plotly.graph_objs as go
import plotly.plotly as py
import requests
from keys import access_token, api_key, consumer_key, stream_ids, username


def int2datetime(datetime_int, date_only=False):
    ret = datetime.datetime.fromtimestamp(datetime_int)
    if date_only:
        ret = ret.replace(hour=0, minute=0, second=0)
        # ret = ret.strftime('%Y-%m-%d')
    else:
        # ret = ret.strftime('%Y-%m-%d %H:%M:%S')
        pass
    return ret


def init():
    """set api_key, username for plotly
    """
    plotly.tools.set_credentials_file(username=username,
                                      api_key=api_key)


def get_archives(since=None):
        """get archives from pocket

        Args:
            since (None, optional): only get archives since the given
                                    since paramerter, or return all

        Returns:
            json: archive data

        Raises:
            'Cannot: Description
        """
        parameters = {'consumer_key': consumer_key,
                      'access_token': access_token,
                      'state': 'archive'}
        if since:
            parameters['since'] = since

        ret = requests.get('https://getpocket.com/v3/get',
                           params=parameters)
        if ret.ok:
            return ret.json()
        raise 'Cannot get archive data'


def existed_data():
    """read existed data from the local file

    Returns:
        json: stored data or None when file doest't exist
    """
    try:
        data = json.load(open('data.json'))
        return data
    except FileNotFoundError:
        return None


def save_data(data):
    """save data to a local file

    Args:
        data (json): json data retrieved from pocket
    """
    with open('data.json', 'w') as output_file:
        json.dump(data, output_file, indent=2)


def merge_json(data1, data2):
    """merge lists in two json data together

    Args:
        data1 (json or None): first json data
        data2 (json): 2nd json data

    Returns:
        TYPE: merged data
    """
    if not data1:
        return data2
    else:
        for i in data2['list']:
            data1['list'][i] = data2['list'][i]
        return data1


def retrieve_data():
    data = existed_data()
    if data:
        since = max([data['list'][i]['time_read'] for i in data['list']])
    else:
        since = None
    new_data = get_archives(since=since)
    merge_json(data, new_data)
    save_data(data)
    plot_data = [(data['list'][i]['time_read'], data['list'][i]['word_count'])
                 for i in data['list'] if 'word_count' in data['list'][i]]
    return sorted(plot_data, key=lambda x: x[0])


def plot(data):
    data = [(int2datetime(int(i[0]), True), int(i[1])) for i in data]
    aggregated_data = defaultdict(int)
    for i in data:
        aggregated_data[i[0]] += i[1]
    aggregated_data = sorted([(k, v) for k, v in aggregated_data.items()])
    x = [i[0] for i in aggregated_data]
    y = [i[1] for i in aggregated_data]
    y_ave = [sum(y[:i + 1]) / ((x[i] - x[0]).days + 1) for i in range(len(y))]
    daily_reading = go.Bar(x=x, y=y, name='Daily Reading')
    average_reading = go.Scatter(x=x, y=y_ave,
                                 name='Average Reading', mode='lines',
                                 yaxis='y2')
    data = [daily_reading, average_reading]
    layout = go.Layout(
        title="How Many Words I've read on Pocket",
        yaxis=dict(
            title='Daily',
            range=[0, 50000]
        ),
        yaxis2=dict(
            title='Average',
            overlaying='y',
            side='right',
            range=[0, 50000]
        ),
        xaxis=dict(
            range=[x[1], x[-1]]
        )
    )
    fig = go.Figure(data=data, layout=layout)
    return py.plot(fig,
                   auto_open=False,
                   filename="How Many Words I've read on Pocket")


def main():
    init()
    data = retrieve_data()
    print(plot(data))


if __name__ == '__main__':
    main()

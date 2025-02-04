import os
import subprocess
import pickle
import time

'''
This is old code used by dataset_rebuild. The newer execnet code
(facemodel_worker) is probably more reliable.
'''


def facemodel_server_start():
    if not os.path.exists('models/facemodel/model.t7'):
        url = 'https://www.dropbox.com/s/18s63zomyfacjfs/facemodel.t7?dl=1'
        subprocess.check_call(['wget', url, '-O', 'models/facemodel/model.t7'])
    os.chdir('models/facemodel')
    try:
        p = subprocess.Popen(['python', '-u', 'server.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             close_fds=True)

    finally:
        os.chdir('../..')
    return p


def facemodel_server_predict(p, ipath):
    pickled = pickle.dumps('../../' + ipath)

    p.stdin.write(pickled)
    rawdata = p.stdout.read()
    if rawdata:
        scores = pickle.loads(rawdata)
        return scores


def facemodel_server_stop(p):
    print(pickle.dumps(None).encode('string_escape'), file=p.stdin)


def facemodel_server_finally(p):
    retcode = p.poll()
    if retcode is None:
        p.terminate()
        time.sleep(0.001)
        retcode = p.poll()
        if retcode is None:
            p.kill()
    else:
        if retcode != 0:
            raise subprocess.CalledProcessError(retcode, 'facemodel server returned non-zero exit status {}'.format(retcode))

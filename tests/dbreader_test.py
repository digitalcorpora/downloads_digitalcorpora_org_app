import sys
import os

from os.path import abspath,dirname

sys.path.append( dirname(dirname(abspath(__file__))))

import bottle_app

def test_dbreader():
    dbreader = bottle_app.get_dbreader()
    assert dbreader is not None
    return dbreader

if __name__=='__main__':
    print("testing dbreader for AWS Secrets")
    bottle_app.aws_setup()
    dbreader = test_dbreader()
    print(f"Successfully obtained dbreader under AWS.")

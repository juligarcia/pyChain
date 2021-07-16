from flask import Flask, request, render_template, redirect
import requests
import json
from pyChain import *
import datetime

app = Flask(__name__)

blockchain = BlockChain()
peers = set()

"""
Modelo:

Transaccion:
  {
    "author": "nombre_del_autor",
    "content": "Algunos pensamientos que el autor quiere compartir",
    "timestamp": "El tiempo en el que el contenido fue creado"
  }
"""


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
  receivedData = request.get_json()
  requiredFields = ['author', 'content']

  for field in requiredFields:
    if not receivedData.get(field):
      return 'Invlaid transaction data', 404

  receivedData['timestamp'] = time.time()

  blockchain.addNewTransaction(receivedData)

  return 'Success', 201


@app.route('/chain', methods=['GET'])
def chain():
  onChainData = []
  for block in blockchain.chain:
    onChainData.append(block.__dict__)
  return json.dumps({'length': len(onChainData), 'chain': onChainData, 'peers': list(peers)})


@ app.route('/mine', methods=['GET'])
def mine():
  print('--- entra ----', peers)
  result = blockchain.mine()
  if not result:
    return 'Can not mine: no transactions or invalid block'

  chainLength = len(blockchain.chain)
  consensus()

  if chainLength == len(blockchain.chain):
    announceBlock(blockchain.lastBlock)

  return "Block #{} mined.".format(result)


@ app.route('/pending')
def pending():
  return json.dumps(blockchain.unconfirmedTransactions)


@app.route('/register_node', methods=['POST'])
def register_new_peers():
  node_address = request.get_json()['node_address']
  if not node_address:
    return 'Invalid data', 400

  peers.add(node_address)

  return chain()


@app.route('/register', methods=['POST'])
def register():
  nodeAddress = request.get_json()['node_address']
  print(request)
  if not nodeAddress:
    return 'Invalid data', 400

  data = {'node_address': request.host_url}
  headers = {'Content-Type': 'application/json'}

  response = requests.post(
      nodeAddress + '/register_node',
      data=json.dumps(data), headers=headers
  )

  if response.status_code == 200:
    global blockchain
    global peers
    chainDump = response.json()['chain']
    blockchain = createChain(chainDump)
    peers.update(response.json()['peers'])
    return 'Registration successful\n', 200
  else:
    return response.content, response.status_code


def createChain(chainDump):
  newBlockchain = BlockChain()
  for i, block_data in enumerate(chainDump):
    if i == 0:
      continue
    block = Block(
        block_data["index"],
        block_data["transactions"],
        block_data["timestamp"],
        block_data["previousHash"],
        block_data["nonce"]
    )
    success = newBlockchain.addBlock(block)
    if not success:
      raise Exception("The chain dump is tampered!!")
  return newBlockchain


def consensus():
  global blockchain

  longestChain = None
  currentLen = len(blockchain.chain)

  for peer in peers:
    response = requests.get('{}chain'.format(peer))
    length = response.json()['length']
    print(length)
    chain = response.json()['chain']
    if length > currentLen and blockchain.checkChainValidity(chain):
      currentLen = length
      longestChain = chain

  if longestChain:
    blockchain = longestChain
    return True

  return False


@ app.route('/add_block', methods=['POST'])
def add_block():
  blockData = request.get_json()
  block = Block(
      blockData['index'], blockData['transactions'],
      blockData['timestamp'], blockData['previousHash']
  )

  success = blockchain.addBlock(block)

  if not success:
    return 'The block was discarded by the node', 400

  return 'Block added to the chain', 201


def announceBlock(block):
  for peer in peers:
    url = '{}add_block'.format(peer)
    requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:8000'

posts = []


def fetchPosts():
  getChainURL = '{}/chain'.format(CONNECTED_NODE_ADDRESS)
  response = requests.get(getChainURL)
  if response.status_code == 200:
    content = []
    chain = json.loads(response.content)
    for block in chain['chain']:
      for transaction in block['transactions']:
        transaction['index'] = block['index']
        transaction['hash'] = block['previousHash']
        content.append(transaction)

    global posts
    posts = sorted(
        content, key=lambda transaction: transaction['timestamp'],
        reverse=True
    )


@app.route('/')
def index():
  fetchPosts()
  return render_template(
      'index.html',
      title='PyChain',
      posts=posts,
      node_address=CONNECTED_NODE_ADDRESS,
      readable_time=timeStampToString
  )


@ app.route('/submit', methods=['POST'])
def submit_block():
  blockContent = request.form['content']
  author = request.form['author']

  post_object = {
      'author': author,
      'content': blockContent,
  }

  newTransactionPostURL = '{}/new_transaction'.format(CONNECTED_NODE_ADDRESS)

  requests.post(
      newTransactionPostURL,
      json=post_object,
      headers={'Content-type': 'application/json'}
  )

  return redirect('/')


def timeStampToString(time):
  return datetime.datetime.fromtimestamp(time).strftime('%H:%M')

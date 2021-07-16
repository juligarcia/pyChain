from hashlib import sha256
import json
import time

class Block:
  def __init__(self, index, transactions, timestamp, previousHash, nonce = 0):
    self.index = index
    self.transactions = transactions
    self.timestamp = timestamp
    self.previousHash = previousHash
    self.nonce = nonce
    self.computeHash()

  def computeHash(self):
    string = json.dumps(self.__dict__, sort_keys=True)
    self.hash = sha256(string.encode()).hexdigest()
    return self.hash

  def setNonce(self, nonce):
    self.nonce = nonce

  def incNonce(self):
    self.nonce += 1
    self.computeHash()

  def getHash(self):
    return self.hash

  def getIndex(self):
    return self.index


class BlockChain:
  def __init__(self):
    self.unconfirmedTransactions = []
    self.chain = []
    self.createGenesisBlock()
    self.difficulty = 3

  def createGenesisBlock(self):
    genesisBlock = Block(0, [], time.time(), 'Genesis')
    genesisBlock.computeHash()
    self.chain.append(genesisBlock)

  def checkChainValidity(self):
    for block in self.chain:
      if not self.self.isValidProof(block):
        return False
    
    return True

  def proofOfWork(self, block: Block):
    while not block.getHash().startswith('0' * self.difficulty):
      block.incNonce()

  @property
  def lastBlock(self):
    return self.chain[-1]

  def isValidProof(self, block: Block):
    return block.getHash().startswith('0' * self.difficulty)

  def addBlock(self, block: Block):
    if self.lastBlock.getHash() != block.previousHash or not self.isValidProof(block):
      return False

    self.chain.append(block)
    return True

  def addNewTransaction(self, transaction):
    self.unconfirmedTransactions.append(transaction)

  def mine(self):
    if not len(self.unconfirmedTransactions):
      return False

    lastBlock = self.lastBlock
    newBlock = Block(
        self.lastBlock.getIndex() + 1,
        self.unconfirmedTransactions,
        time.time(),
        lastBlock.getHash()
    )

    self.proofOfWork(newBlock)
    self.addBlock(newBlock)
    self.unconfirmedTransactions = []

    return newBlock.getIndex()

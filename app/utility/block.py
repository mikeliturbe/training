# https://github.com/satwikkansal/python_blockchain_app/blob/ibm_blockchain_post/node_server.py
import hashlib
import json
import time


class Block:

    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        """
        Constructor for the Block class
        :param index: Unique ID of the block
        :param transactions: List of the transactions in the chain
        :param timestamp: Time of generation of the block
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        block = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block.encode()).hexdigest()


class BlockChain:

    difficulty = 2

    @property
    def last_block(self):
        return self.chain[-1]

    def __init__(self):
        self.chain = []
        self.unconfirmed_transactions = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if (previous_hash != block.previous_hash) or (not self.is_valid_proof(block, proof)):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        block = Block(index=last_block.index+1,
                      transactions=self.unconfirmed_transactions,
                      timestamp=time.time(),
                      previous_hash=last_block.hash)
        self.add_block(block, self.proof_of_work(block))
        self.unconfirmed_transactions = []
        return block.index

    @staticmethod
    def proof_of_work(block):
        block.nonce = 0
        c_hash = block.compute_hash()
        while not c_hash.startswith('0' * BlockChain.difficulty):
            block.nonce += 1
            c_hash = block.compute_hash()
        return c_hash

    @classmethod
    def is_valid_proof(cls, block, b_hash):
        return (b_hash.startswith('0' * BlockChain.difficulty)) and (b_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = '0'
        for block in chain:
            block_hash = block.hash
            delattr(block, 'hash')
            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                result = False
                break
            block.hash, previous_hash = block_hash, block_hash
        return result

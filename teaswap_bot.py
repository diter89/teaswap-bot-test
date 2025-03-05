import asyncio
import logging
import os
from typing import Dict, List
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from swaps_tokens.tea_to_contract import TeaToContract


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


POPULAR_TOKENS: List[Dict] = [
    {"address": "0xf990e015F8DAEf9F7d51B6d57c6E105D9bd5f3be", "name": "butt"},
    {"address": "0xdD777582C445f234d3E2C6c3B3a9dd1dDf3558F1", "name": "Fresh Tea"},
    {"address": "0x623769444c1BA04c55A4690bDD2955cD4f089bb7", "name": "Blurtopian"},
    {"address": "0x1B54e5BBb545245f4c468929D64dAbb479aE055e", "name": "CLW"},
    {"address": "0xcC431866D471096a2cD4A24790128202B8Ee0E86", "name": "ANIME"},
    {"address": "0x15B7e0AF94F36aB8dBFd8ED6fd56edc0a3a73683", "name": "winner tea"},
    {"address": "0x81fB2b0D74F4B0148Ea08d0Eb65b99f187A393E3", "name": "TRUMP BIG TOKEN"},
    {"address": "0x2F3754Cb1F05fE6701C76603B1c69830347F5B3A", "name": "YERIM"},
    {"address": "0x7987954bb6aC6b79819b08bFC268917AD38E12c6", "name": "Teaalien"},
    {"address": "0x03C5273a766efC2DFb5205342B742d5E5f02d755", "name": "Manchester United"},
    {"address": "0x90f7C3F1043D595B88849Ca45b81763636Ac9dB9", "name": "RS"},
    {"address": "0x42c6698Ae5537E7a7760d313244d75f09D45D7A2", "name": "Lemon Tea"},
    {"address": "0x7f9FA637886eAb2C67c05d3087C6de92343af807", "name": "tea ea"},
    {"address": "0xc998F150999acaC9CdC311CC739c869FEBC01A65", "name": "Assam Tea"},
    {"address": "0xd8681C1F60Ba30982292CD22982Aa2A9f30adf2c", "name": "Airdrop Intelligent Testnet"},
    {"address": "0x19dab75B9D703f5a7e176CD08d5A29676aaB94fc", "name": "MeowTea Token"},
    {"address": "0x50dCB6e1f907632Fb145459faCE86E358c1Cfb0B", "name": "Assam AI Alliance"},
    {"address": "0xB6FD54D9102422f8D167C82803f875CD914d08bB", "name": "Gula"},
    {"address": "0xC4341CB2C976306AE9169efb3d8301ea287a3128", "name": "BITCOIN"},
    {"address": "0x9faE22428bBA5De88730e9C7Ccab79c8d1Ac34E5", "name": "Tea USD"},
]

class SwapConfig(StatesGroup):
    contract_address = State()
    gasprice = State()
    amount = State()

class SwapBot:
    def __init__(self):
        self.TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables!")
        
        self.PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
        if not self.PRIVATE_KEY:
            raise ValueError("PRIVATE_KEY is not set in environment variables!")
        
        self.USER_ADDRESS = os.environ.get("USER_ADDRESS")
        if not self.USER_ADDRESS:
            raise ValueError("USER_ADDRESS is not set in environment variables!")
        
        self.contract_address = os.environ.get("CONTRACT_ADDRESS", "0xC4341CB2C976306AE9169efb3d8301ea287a3128")
        self.gasprice = int(os.environ.get("GAS_PRICE", 1000))
        self.amount = float(os.environ.get("AMOUNT", 1.0))

        self.bot = Bot(token=self.TOKEN)
        self.dp = Dispatcher()

        self.assam = TeaToContract(
            private_key=self.PRIVATE_KEY,
            user_address=self.USER_ADDRESS,
            contract_address=self.contract_address,
            gasprice=self.gasprice,
            amount=self.amount,
        )

    def format_result(self, result: Dict) -> str:
        swap_tx_hash = result.get('swap_tx_hash', 'N/A')
        swap_tx_link = f"https://assam.tea.xyz/tx/{swap_tx_hash}" if swap_tx_hash != "N/A" else "#"
        return f"""
<b>🔹 Swap Transaction Result:</b>
🔹 <b>Tea Balance:</b> <code><pre>{result.get('tea_balance_tokens', 'N/A')}</pre></code>
🔹 <b>WTea Balance:</b> <code><pre>{result.get('wtea_balance_tokens', 'N/A')}</pre></code>
🔹 <b>Wrap TX Hash:</b> <code>{result.get('wrap_tx_hash', 'N/A')}</code>
🔹 <b>Approval TX Hash:</b> <code>{result.get('approval_tx_hash', 'N/A')}</code>
🔹 <b>Swap TX Hash:</b> <a href="{swap_tx_link}">{swap_tx_hash}</a>
🔹 <b>Status:</b> ✅ {result.get('swap_status', 'N/A')}
🔹 <b>Message:</b> {result.get('message', 'N/A')}
"""

    def main_menu(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💱 Swap", callback_data="swap")],
            [InlineKeyboardButton(text="📜 Set Contract", callback_data="set_contract")],
            [InlineKeyboardButton(text="⛽ Set Gas Price", callback_data="set_gasprice")],
            [InlineKeyboardButton(text="📏 Set Amount", callback_data="set_amount")],
            [InlineKeyboardButton(text="🏅 Show Popular Tokens", callback_data="show_popular")],
            [InlineKeyboardButton(text="❓ Help", callback_data="help")]
        ])
        return keyboard

    def format_popular_tokens(self) -> str:
        token_list = "<b>🏅 Popular Tokens List:</b>\n\n"
        for token in POPULAR_TOKENS:
            token_list += f"🔹 <b>{token['name'].upper()}</b>: <code><i>{token['address']}</i></code>\n"
        return token_list

    async def run(self):
        await self.dp.start_polling(self.bot)

    def register_commands(self):
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                "🔹 Welcome to Swap Tea Assam Bot!\n"
                "Use the buttons below to interact:",
                reply_markup=self.main_menu()
            )

        @self.dp.callback_query(lambda c: c.data == "swap")
        async def process_swap(callback: types.CallbackQuery):
            try:
                result = self.assam.eksekusi()
                logger.info(f"Swap result: {result}")
                formatted_result = self.format_result(result)
                await callback.message.answer(formatted_result, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Swap failed: {str(e)}")
                await callback.message.answer(f"❌ Error: {str(e)}")
            await callback.answer()

        @self.dp.callback_query(lambda c: c.data == "set_contract")
        async def set_contract(callback: types.CallbackQuery, state: FSMContext):
            await callback.message.answer("📝 Enter new contract address:")
            await state.set_state(SwapConfig.contract_address)
            await callback.answer()

        @self.dp.message(SwapConfig.contract_address)
        async def process_contract_address(message: Message, state: FSMContext):
            new_contract = message.text.strip()
            self.assam.contract_address = new_contract
            self.contract_address = new_contract
            logger.info(f"Contract address updated to {new_contract}")
            await state.clear()
            await message.answer(f"✅ Contract Address updated:\n<code>{new_contract}</code>", parse_mode="HTML")

        @self.dp.callback_query(lambda c: c.data == "set_gasprice")
        async def set_gasprice(callback: types.CallbackQuery, state: FSMContext):
            await callback.message.answer("📝 Enter new gas price (in numbers):")
            await state.set_state(SwapConfig.gasprice)
            await callback.answer()

        @self.dp.message(SwapConfig.gasprice)
        async def process_gasprice(message: Message, state: FSMContext):
            try:
                new_gasprice = int(message.text.strip())
                self.assam.gasprice = new_gasprice
                self.gasprice = new_gasprice
                logger.info(f"Gas price updated to {new_gasprice}")
                await state.clear()
                await message.answer(f"✅ Gas Price updated: <b>{new_gasprice}</b>", parse_mode="HTML")
            except ValueError:
                await message.answer("❌ Please enter a valid number.")

        @self.dp.callback_query(lambda c: c.data == "set_amount")
        async def set_amount(callback: types.CallbackQuery, state: FSMContext):
            await callback.message.answer("📝 Enter new amount (e.g., 1.5):")
            await state.set_state(SwapConfig.amount)
            await callback.answer()

        @self.dp.message(SwapConfig.amount)
        async def process_amount(message: Message, state: FSMContext):
            try:
                new_amount = float(message.text.strip())
                self.assam.amount = new_amount
                self.amount = new_amount
                logger.info(f"Amount updated to {new_amount}")
                await state.clear()
                await message.answer(f"✅ Amount updated: <b>{new_amount}</b>", parse_mode="HTML")
            except ValueError:
                await message.answer("❌ Please enter a valid number (e.g., 1.5).")

        @self.dp.callback_query(lambda c: c.data == "show_popular")
        async def show_popular_tokens(callback: types.CallbackQuery):
            formatted_tokens = self.format_popular_tokens()
            await callback.message.answer(formatted_tokens, parse_mode="HTML")
            await callback.answer()

        @self.dp.callback_query(lambda c: c.data == "help")
        async def cmd_help(callback: types.CallbackQuery):
            await callback.message.answer(
                "📌 <b>Usage Instructions:</b>\n"
                "💱 <b>Swap</b> - Execute swap transaction\n"
                "📜 <b>Set Contract</b> - Change contract address\n"
                "⛽ <b>Set Gas Price</b> - Change gas price\n"
                "📏 <b>Set Amount</b> - Change swap amount\n"
                "🏅 <b>Show Popular Tokens</b> - Display popular tokens list\n"
                "❓ <b>Help</b> - Show this help message",
                parse_mode="HTML"
            )
            await callback.answer()

if __name__ == "__main__":
    bot = SwapBot()
    bot.register_commands()
    print("Bot is running...")
    asyncio.run(bot.run())

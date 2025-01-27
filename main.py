import re
import asyncio
from telethon import TelegramClient

# API ID dan API Hash dari my.telegram.org
api_id = "24655300"
api_hash = "62f84d7c53030e6d5ede4caf8c9c2f17"

# Nama session untuk login
session_name = "L_Biru"

# Buat client Telethon
client = TelegramClient(session_name, api_id, api_hash)

# Regex pattern untuk menangkap informasi penting
pattern = r"(Buy|Sell).*?Highrisk@([\d\-]+)|SL[-:\s]+(\d+)|TP1[-:\s]+(\d+)|TP2[-:\s]+(\d+)|TP3[-:\s]+(\d+)"

# Nama file untuk menyimpan dua pesan terakhir
file_name = "file.txt"

# Set untuk menyimpan pesan yang sudah dikirim
sent_messages = set()


def save_to_file(messages):
    """
    Menyimpan dua pesan terakhir ke file.
    :param messages: List pesan untuk disimpan
    """
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n\n".join(messages))
    print("[INFO] Dua pesan terakhir disimpan ke file.txt")


def read_from_file():
    """
    Membaca isi file.
    :return: Isi file sebagai list
    """
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read().split("\n\n")
    except FileNotFoundError:
        print("[INFO] file.txt tidak ditemukan, membuat file baru.")
        return []


def process_message(message_text):
    """
    Memproses pesan dengan regex untuk menangkap informasi penting.
    :param message_text: Teks pesan yang akan diproses
    :return: Pesan hasil filter yang siap dikirim, atau None jika tidak sesuai format
    """
    matches = re.finditer(pattern, message_text)

    # Variabel untuk menyimpan data yang ditemukan
    signal, sl, tp1, tp2, tp3 = "", "", "", "", ""

    for match in matches:
        if match.group(1):  # Buy/Sell
            signal = f"Signal: {match.group(1)} Highrisk@{match.group(2)}"
        if match.group(3):  # SL
            sl = f"SL: {match.group(3)}"
        if match.group(4):  # TP1
            tp1 = f"TP1: {match.group(4)}"
        if match.group(5):  # TP2
            tp2 = f"TP2: {match.group(5)}"
        if match.group(6):  # TP3
            tp3 = f"TP3: {match.group(6)}"

    # Gabungkan hasil menjadi satu pesan
    filtered_data = ["Entry: XAUUSD", signal, sl, tp1, tp2, tp3]
    result = "\n".join([data for data in filtered_data if data])

    # Hanya kembalikan pesan jika sesuai format
    return result if signal and sl and tp1 else None


async def fetch_and_process_messages(channel_username, target_chat):
    """
    Mengambil pesan terbaru dari channel, memperbarui file, dan mengirim pesan jika ada yang baru dan sesuai format.
    :param channel_username: Username channel sumber
    :param target_chat: Username bot/channel tujuan
    """
    while True:
        try:
            # Ambil pesan terbaru dari channel
            messages = []
            async for message in client.iter_messages(channel_username, limit=2):
                if message.text:
                    processed = process_message(message.text)
                    if processed:  # Tambahkan hanya jika pesan sesuai format
                        messages.append(processed)

            # Jika ada pesan, perbarui file
            if messages:
                messages.reverse()  # Urutkan pesan dari yang paling lama
                save_to_file(messages)

                # Baca pesan dari file
                saved_messages = read_from_file()

                # Kirim pesan jika ada yang baru
                for msg in saved_messages:
                    if msg not in sent_messages:
                        print(f"[INFO] Mengirim pesan: {msg}")
                        await client.send_message(target_chat, msg)
                        sent_messages.add(msg)  # Tandai pesan sebagai sudah dikirim

        except Exception as e:
            print(f"[ERROR] Terjadi kesalahan: {e}")

        await asyncio.sleep(1)  # Tunggu 1 detik sebelum memeriksa ulang


async def main():
    channel_username = "linktestsignal"  # Channel sumber
    target_chat = "SignalGoldBosskuhhBot"  # Bot/channel tujuan

    print("[INFO] Bot sedang berjalan... Tekan Ctrl+C untuk menghentikan.")
    await fetch_and_process_messages(channel_username, target_chat)


# Jalankan client
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())

import pygame
import numpy as np
import random
from abc import ABC, abstractmethod

class GameWorld:
    def __init__(self, size):
        self.size = size
        self.matrix = np.full((size, size), '.', dtype=str)  # Başlangıçta tüm hücreler boş
        self.player_colors = {}  # Oyuncuların renklerini depolamak için bir sözlük

    def place_warrior(self, row, col, warrior, player_color):
        if 0 <= row < self.size and 0 <= col < self.size:
            self.matrix[row, col] = warrior.get_symbol()
            self.player_colors[(row, col)] = player_color  # Oyuncunun rengini depola
        else:
            print("Geçersiz hücre koordinatları.")
class Savaşçı(ABC):
    def __init__(self, sembol, renk):
        self.sembol = sembol
        self.renk = renk

    def get_symbol(self):
        return self.sembol

    def get_color(self):
        return self.renk

class Muhafız(Savaşçı):
    def __init__(self):
        super().__init__('M', (255, 0, 0))  # Kırmızı renk

    def saldırı_yap(self, game_world, row, col):
        # Muhafızın saldırı menzili (yatay, dikey ve çapraz olarak 1 hücre)
        menzil = [(row + i, col + j) for i in range(-1, 2) for j in range(-1, 2)]

        # Hedefteki düşmanları bul
        hedefler = []
        for r, c in menzil:
            if 0 <= r < game_world.size and 0 <= c < game_world.size:
                if game_world.matrix[r, c] != '.' and game_world.matrix[r, c] != self.get_symbol():
                    hedefler.append((r, c))

        # Hedefteki düşmanlara saldır
        for hedef_row, hedef_col in hedefler:
            game_world.matrix[hedef_row, hedef_col] = '.'  # Düşmanı yok et
            print(f"Muhafız {self.get_symbol()} {hedef_row}-{hedef_col} hedefine saldırdı!")

class Okçu(Savaşçı):
    def __init__(self):
        super().__init__('O', (0, 0, 255))  # Mavi renk

    def saldırı_yap(self, game_world, row, col):
        # Okçu sadece en yüksek cana sahip 3 düşmanı hedef alır
        # düşmanları ve can değerleri için liste
        düşmanlar = []
        for i in range(game_world.size):
            for j in range(game_world.size):
                if game_world.matrix[i, j] != '.' and game_world.matrix[i, j] != self.get_symbol():
                    düşmanlar.append((i, j, game_world.matrix[i, j]))

        # Listeyi can değerine göre sıralayarak en yüksek cana sahip 3 düşmanı seçelim
        hedefler = sorted(düşmanlar, key=lambda x: x[2], reverse=True)[:3]

        # Seçilen hedeflere saldır
        for hedef in hedefler:
            hedef_row, hedef_col, _ = hedef
            game_world.matrix[hedef_row, hedef_col] = '.'  # Düşmanı yok et
            print(f"Okçu {self.get_symbol()} {hedef_row}-{hedef_col} hedefine saldırdı!")

class Topçu(Savaşçı):
    def __init__(self):
        super().__init__('T', (0, 255, 0))  # Yeşil renk

    def saldırı_yap(self, game_world, row, col):
        # Topçu sadece en yüksek cana sahip 1 düşmanı hedef alır
        #  düşmanlar ve can değerleri için liste
        düşmanlar = []
        for i in range(game_world.size):
            for j in range(game_world.size):
                if game_world.matrix[i, j] != '.' and game_world.matrix[i, j] != self.get_symbol():
                    düşmanlar.append((i, j, game_world.matrix[i, j]))

        # Listeyi can değerine göre sıralayarak en yüksek cana sahip düşmanı seçelim
        en_yüksek_canlı = max(düşmanlar, key=lambda x: x[2])

        # En yüksek cana sahip düşmana saldır
        hedef_row, hedef_col, _ = en_yüksek_canlı
        game_world.matrix[hedef_row, hedef_col] = '.'  # Düşmanı yok et
        print(f"Topçu {self.get_symbol()} {hedef_row}-{hedef_col} hedefine saldırdı!")
class Atlı(Savaşçı):
    def __init__(self):
        super().__init__('A', (255, 255, 0))  # Sarı renk

    def saldırı_yap(self, game_world, row, col):
        # Atlı, menzil içerisindeki en pahalı 2 düşmanı hedef alır
        menzil = [(row + i, col + j) for i in range(-3, 4) for j in range(-3, 4)
                  if (i, j) != (0, 0) and abs(i) + abs(j) <= 3]  # Menzili belirle

        # Menzil içindeki düşmanlar ve can değerler için liste
        düşmanlar = []
        for r, c in menzil:
            if 0 <= r < game_world.size and 0 <= c < game_world.size:
                if game_world.matrix[r, c] != '.' and game_world.matrix[r, c] != self.get_symbol():
                    düşmanlar.append((r, c, game_world.matrix[r, c]))

        # Listeyi can değerlerine göre sırala ve en pahalı 2 taneyi seç
        en_pahalılar = sorted(düşmanlar, key=lambda x: x[2], reverse=True)[:2]

        # En pahalı 2 düşmana saldır
        for hedef_row, hedef_col, _ in en_pahalılar:
            game_world.matrix[hedef_row, hedef_col] = '.'  # Düşmanı yok et
            print(f"Atlı {self.get_symbol()} {hedef_row}-{hedef_col} hedefine saldırdı!")

class Sağlıkçı(Savaşçı):
    def __init__(self):
        super().__init__('S', (255, 255, 255))  # Beyaz renk

    def dost_can_artir(self, game_world, row, col):
        # Sağlıkçının menzili içindeki dost birlikleri bul
        menzil = [(row + i, col + j) for i in range(-2, 3) for j in range(-2, 3) if 0 <= row + i < game_world.size and 0 <= col + j < game_world.size]
        dostlar = []
        for r, c in menzil:
            if 0 <= r < game_world.size and 0 <= c < game_world.size:
                if game_world.matrix[r, c] != '.' and game_world.matrix[r, c] == self.get_symbol():
                    dostlar.append((r, c))

        # Dost birliklerin canını artır
        for dost_row, dost_col in dostlar:
            if game_world.matrix[dost_row, dost_col] == self.get_symbol():
                # Dost birliğin canını artır
                if game_world.matrix[dost_row, dost_col].can + 50 <= 100:
                    game_world.matrix[dost_row, dost_col].can += 50
                else:
                    game_world.matrix[dost_row, dost_col].can = 100
                print(f"Sağlıkçı {self.get_symbol()} {dost_row}-{dost_col} konumundaki dost birliğin canını artırdı!")
def get_world_size():
    while True:
        try:
            size = int(input("Oyun alanı boyutunu girin (örneğin, 8x8 için 8): "))
            if size < 8 or size > 32:  # Boyutun 8x8 ile 32x32 arasında olması gerekiyor
                print("Boyut 8x8 ile 32x32 arasında olmalıdır.")
            else:
                return size
        except ValueError:
            print("Geçersiz bir değer girdiniz. Lütfen bir tamsayı girin.")

def get_player_count():
    while True:
        try:
            player_count = int(input("Oyuncu sayısını girin (minimum 1, maksimum 4): "))
            if player_count < 1 or player_count > 4:
                print("Oyuncu sayısı 1 ile 4 arasında olmalıdır.")
            else:
                return player_count
        except ValueError:
            print("Geçersiz bir değer girdiniz. Lütfen bir tamsayı girin.")

def determine_player_order(player_count):
    order = list(range(1, player_count + 1))  # Oyuncu numaraları
    random.shuffle(order)  # Rastgele sıralama
    return order

# Oyun alanı boyutunu kullanıcıdan al
world_size = get_world_size()

# Oyun alanı boyutunu kullanıcıdan aldıktan sonra köşeleri oluştur
corners = [(0, 0), (0, world_size - 1), (world_size - 1, 0), (world_size - 1, world_size - 1)]

# Oyun dünyasını oluştur
game_world = GameWorld(world_size)

# Oyuncu sayısını belirle
player_count = get_player_count()
print("Oyuncu sayısı:", player_count)

# Oyuncuların sırasını belirle
player_order = determine_player_order(player_count)
print("Oyuncu sırası:", player_order)

def place_warriors(game_world, player_order):
    colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]  # Oyuncu renkleri: Kırmızı, Mavi, Yeşil, Sarı
    for player_num in player_order:
        player_color = colors[player_num - 1]  # Oyuncunun rengini al
        print(f"Oyuncu {player_num}'in savaşçıları ({player_color}):")

        # Rastgele bir köşe seç
        corner_row, corner_col = random.choice(
            [(0, 0), (0, game_world.size - 1), (game_world.size - 1, 0), (game_world.size - 1, game_world.size - 1)])

        # Muhafızı rastgele köşeye yerleştir
        game_world.place_warrior(corner_row, corner_col, Muhafız(), player_color)

        for i in range(2):  # Her oyuncu en fazla 2 savaşçı yerleştirebilir
            print(f"Savaşçı seçimi {i + 1}:")
            warrior_type = input("Savaşçı türünü seçin (Muhafız, Okçu, Topçu, Atlı, Sağlıkçı): ").strip().lower()
            row = int(input("Yerleştirmek istediğiniz satır numarasını girin: "))
            col = int(input("Yerleştirmek istediğiniz sütun numarasını girin: "))

            # Seçilen savaşçı türüne göre nesne oluşturulması
            if warrior_type == "muhafız":
                warrior = Muhafız()
            elif warrior_type == "okçu":
                warrior = Okçu()
            elif warrior_type == "topçu":
                warrior = Topçu()
            elif warrior_type == "atlı":
                warrior = Atlı()
            elif warrior_type == "sağlıkçı":
                warrior = Sağlıkçı()
            else:
                print("Geçersiz savaşçı türü.")
                continue

            # Oyuncunun seçtiği koordinatlara savaşçının yerleştirilmesi
            game_world.place_warrior(row, col, warrior, player_color)

# Savaşçıları yerleştir
place_warriors(game_world, player_order)

# Köşeleri oluştur
corners = [(0, 0), (0, world_size - 1), (world_size - 1, 0), (world_size - 1, world_size - 1)]
random.shuffle(corners)  # Köşeleri karıştır

class Hazine:
    def __init__(self):
        self.kaynak = 200  # Başlangıçta her oyuncunun 200 kaynağı var
        self.can = 1  # Her oyuncunun başlangıçta 1 canı var

    def harcayabilir_mi(self, miktar):
        return self.kaynak >= miktar

    def kaynak_harcama(self, miktar):
        if self.harcayabilir_mi(miktar):
            self.kaynak -= miktar
            return True
        else:
            return False

    def can_azalt(self):
        self.can -= 1

# Oyuncuları temsil etmek için bir sözlük
oyuncular = {}

# Her oyuncu için bir hazine oluşturuldu ve oyuncu sözlüğüne eklendi
for player_num in player_order:
    oyuncular[player_num] = Hazine()


# Pygame başlat
pygame.init()

# Ekran boyutu
SCREEN_SIZE = 600
CELL_SIZE = SCREEN_SIZE // world_size

# Ekranı oluştur
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Oyun Alanı")

# Renkler
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Ana döngü
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Ekranı temizle
    screen.fill((0, 0, 0))  # Siyah renk

    # Oyun dünyasını ekrana çiz
    for i in range(world_size):
        for j in range(world_size):
            cell_content = game_world.matrix[i, j]
            if cell_content == '.':
                color = (0, 0, 0)  # Siyah renk
                pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                font = pygame.font.SysFont(None, 30)
                text = font.render(".", True, (255, 255, 255))  # Beyaz renk
                screen.blit(text, (j * CELL_SIZE + CELL_SIZE // 3, i * CELL_SIZE + CELL_SIZE // 3))
            else:
                for warrior_class in [Muhafız, Okçu, Topçu, Atlı, Sağlıkçı]:
                    if cell_content == warrior_class().get_symbol():
                        color = warrior_class().get_color()
                        pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                        font = pygame.font.SysFont(None, 30)
                        text = font.render(cell_content, True, (255, 255, 255))
                        screen.blit(text, (j * CELL_SIZE + CELL_SIZE // 3, i * CELL_SIZE + CELL_SIZE // 3))

    # Ekranı güncelle
    pygame.display.flip()

# Pygame kapat
pygame.quit()
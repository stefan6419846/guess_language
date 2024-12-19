import itertools
import warnings
from importlib.util import find_spec
from unittest import TestCase

from guess_language import (
    BLOCK_RSHIFT,
    BLOCKS,
    create_ordered_model,
    find_runs,
    guess_language,
    guess_language_id,
    guess_language_info,
    guess_language_name,
    UNKNOWN,
)


class GuessLanguageTestCase(TestCase):
    TESTS = [
        ("", UNKNOWN),
        (
            " ملايين الناخبين الأمريكيين يدلون بأصواتهم وسط إقبال قياسي على "
            "انتخابات هي الأشد تنافسا منذ عقود",
            "ar",
        ),
        (
            "Daxil olan xəbərlərdə deyilir ki, 6 nəfər Bağdadın mərkəzində "
            "yerləşən Təhsil Nazirliyinin binası yaxınlığında baş vermiş "
            "partlayış zamanı həlak olub.",
            "az",
        ),
        (
            "е готов да даде гаранции, че няма да прави ядрено оръжие, ако му "
            "се разреши мирна атомна програма",
            "bg",
        ),
        (
            "Francouzský ministr financí zmírnil výhrady vůči nízkým firemním "
            "daním v nových členských státech EU",
            "cs",
        ),
        (
            "På denne side bringer vi billeder fra de mange forskellige "
            "forberedelser til arrangementet, efterhånden som vi får dem ",
            "da",
        ),
        (
            "αναμένεται να σπάσουν παράδοση δεκαετιών και να συνεχίσουν την "
            "εκστρατεία τους ακόμη και τη μέρα των εκλογών",
            "el",
        ),
        ("This is a test of the language checker.", "en"),
        ("La akcento estas sur la antaŭlasta silabo.", "eo"),
        (
            "La respuesta de los acreedores a la oferta argentina para salir del "
            "default no ha sido muy positiv",
            "es",
        ),
        (
            "Ennetamaks reisil ebameeldivaid vahejuhtumeid vii end kurssi "
            "reisidokumentide ja viisade reeglitega ning muu praktilise "
            "informatsiooniga",
            "et",
        ),
        (
            "on julkishallinnon verkkopalveluiden yhteinen osoite. Kansalaisten "
            "arkielämää helpottavaa tietoa on koottu eri aihealueisiin",
            "fi",
        ),
        ("Vérifions que le détecteur de langue fonctionne.", "fr"),
        (
            "biće prilično izjednačena, sugerišu najnovije ankete. Oba kandidata "
            "tvrde da su sposobni da dobiju rat protiv terorizma",
            "hr",
        ),
        (
            "Hiába jön létre az önkéntes magyar haderő, hiába nem lesz "
            "többé bevonulás, változatlanul fennmarad a hadkötelezettség "
            "intézménye",
            "hu",
        ),
        ("հարաբերական", "hy"),
        (
            "トヨタ自動車、フィリピンの植林活動で第三者認証取得　"
            "トヨタ自動車(株)（以下、トヨタ）は、2007年９月よりフィリピンのルソン"
            "島北部に位置するカガヤン州ペニャブランカ町",
            "ja",
        ),
        (
            "Сайлау нәтижесінде дауыстардың басым бөлігін ел премьер "
            "министрі Виктор Янукович пен оның қарсыласы, оппозиция "
            "жетекшісі Виктор Ющенко алды.",
            "kk",
        ),
        (
            "көрбөгөндөй элдик толкундоо болуп, Кокон шаарынын көчөлөрүндө "
            "бир нече миң киши нааразылык билдирди.",
            "ky",
        ),
        (
            "на јавното мислење покажуваат дека трката е толку тесна, "
            "што се очекува двајцата соперници да ја прекршат традицијата "
            "и да се појават и на самиот изборен ден.",
            "mk",
        ),
        (
            "Nominasjonskomiteen i Akershus KrF har skviset ut Einar Holstad "
            "fra stortingslisten. Ytre Enebakk-mannen har plass p Stortinget "
            "s lenge Valgerd Svarstad Haugland sitter i",
            "nb",
        ),
        (
            "Die kritiek was volgens hem bitter hard nodig, "
            "omdat Nederland binnen een paar jaar in een soort Belfast zou "
            "dreigen te veranderen",
            "nl",
        ),
        ("Sprawdźmy, czy odgadywacz języków pracuje", "pl"),
        (
            "Portugal é um país soberano unitário localizado " "no Sudoeste da Europa.",
            "pt",
        ),
        (
            "în acest sens aparţinînd Adunării Generale a organizaţiei, "
            "în ciuda faptului că mai multe dintre solicitările organizaţiei "
            "privind organizarea scrutinului nu au fost soluţionate",
            "ro",
        ),
        ("авай проверить  узнает ли наш угадатель русски язык", "ru"),
        (
            "kaluan ditën e fundit të fushatës në shtetet kryesore "
            "për të siguruar sa më shumë votues.",
            "sq",
        ),
        (
            "Vi säger att Frälsningen är en gåva till alla, fritt och för "
            "intet.  Men som vi nämnt så finns det två villkor som måste",
            "sv",
        ),
        (
            "yakın tarihin en çekişmeli başkanlık seçiminde oy verme işlemi "
            "sürerken, katılımda rekor bekleniyor.",
            "tr",
        ),
        (
            "Американське суспільство, поділене суперечностями, збирається "
            "взяти активну участь у голосуванні",
            "uk",
        ),
        (
            "милиция ва уч солиқ идораси ходимлари яраланган. Шаҳарда "
            "хавфсизлик чоралари кучайтирилган.",
            "uz",
        ),
        (
            "Hai vấn đề khó chịu với màn hình thường gặp nhất khi bạn dùng "
            "laptop là vết trầy xước và điểm chết. Sau đây là vài cách xử "
            "lý chúng.",
            "vi",
        ),
        ("美国各州选民今天开始正式投票。据信，", "zh"),
    ]

    # Tests with limited possible languages
    TESTS_WITH_HINTS = [
        (
            'Gemälde "Lady Diana" '
            "Original Acryl-Gemälde 60 x 80cm auf Leinwand, gerahmt",
            "de",
            {"de", "en", "fr", "it"},
        ),
    ]

    # Tests that work only when PyEnchant is available.
    ENCHANT_TESTS = [
        ("Guess the language!", "en"),
        (
            "Slovenia, Croatia, Bosnia and Herzegovina, Montenegro, Serbia, "
            "Macedonia, Kosovo, Vojvodina",
            "en",
        ),
    ]

    def test_find_runs(self):
        self.assertEqual(
            ["Basic Latin"],
            find_runs("This is a test of the language checker".split()),
        )
        self.assertEqual(
            {"Basic Latin", "Extended Latin"}, set(find_runs("abcdééé".split()))
        )

        s = (
            "Сайлау нәтижесінде дауыстардың басым бөлігін ел премьер "
            "министрі Виктор Янукович пен оның қарсыласы, оппозиция "
            "жетекшісі Виктор Ющенко алды."
        )
        self.assertEqual(["Cyrillic"], find_runs(s.split()))

    def test_create_ordered_model(self):
        self.assertEqual(["abc"], create_ordered_model("abc"))
        self.assertEqual(["abc", "bca"], create_ordered_model("abca"))
        self.assertEqual(
            ["cab", "abc", "abd", "bca", "bdc", "dca"],
            create_ordered_model("abcabdcab"),
        )

    def test_guess(self):
        for text, name in self.TESTS:
            self.assertEqual(name, guess_language(text))

    def test_guess_with_hints(self):
        for text, name, hints in self.TESTS_WITH_HINTS:
            self.assertEqual(name, guess_language(text, hints))

    def test_guess_tag(self):
        text = "Vérifions que le détecteur de langue fonctionne."
        self.assertEqual("fr", guess_language(text))
        self.assertEqual("French", guess_language_name(text))
        self.assertEqual(26150, guess_language_id(text))
        self.assertEqual(("fr", 26150, "French"), guess_language_info(text))

    def test_guess_enchant(self):
        if not find_spec("enchant"):
            self.skipTest("Enchant not found")

        import enchant

        languages = enchant.list_languages()

        for text, name in self.ENCHANT_TESTS:
            if any(language.startswith(name) for language in languages):
                self.assertEqual(name, guess_language(text))
            else:
                warnings.warn(f"no spelling dictionary for language {name!r}", stacklevel=2)


class BlocksTestCase(TestCase):
    def test_unicode_block(self):
        for n in range(128):
            self.assert_block(n, "Basic Latin")

        for n in itertools.chain(range(0x80, 0x180), range(0x250, 0x2B0)):
            self.assert_block(n, "Extended Latin")

        self.assert_block(0xE00, "Thai")
        self.assert_block(0xE7F, "Thai")
        self.assert_block(0xE80, "Lao")
        self.assert_block(0xEFF, "Lao")
        self.assert_block(0xF00, "Tibetan")
        self.assert_block(0xFFF, "Tibetan")
        self.assert_block(0x421, "Cyrillic")

    def assert_block(self, n, name):
        block = BLOCKS[n >> BLOCK_RSHIFT]
        self.assertEqual(block, name)

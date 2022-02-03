import base64
import os
import string
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone

from inquery.managers import InqueryManager, DesignerManager, InqueryStatusManager, BusyManager, InqueryFileManager

# способ оплаты в заявке
inquery_type_pay = (
    ('cash', 'Оплата наличными'),
    ('card', 'Оплата картой'),
    ('installment', 'Рассрочка'),
    ('perechislenie', 'Перечисление'),
)
# /способ оплаты в заявке

"""Цифровое представление номера телефона (используется в модели 'Client')."""
def clean_number_phone(phone):
    phone = [n for n in phone if n in string.digits]
    return "".join(phone)


class Client(models.Model):
    """Модель для описания потребителя товаров услуг и.т.д."""
    name = models.CharField(max_length=100, verbose_name="Фамилия Имя Отчество")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    phone = models.CharField(max_length=50, verbose_name="Телефон Клиента")
    phone_two = models.CharField(max_length=50, null=True, blank=True, verbose_name="Телефон Клиента2")
    room = models.CharField(max_length=20, verbose_name="Квартира")
    floor = models.CharField(max_length=20, verbose_name="Этаж")
    porch = models.CharField(max_length=5, verbose_name=u"Номер подъезда", blank=True, null=True)

    class Meta:
        default_permissions = []
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __unicode__(self):
        return u"{0} {1}".format(self.name, self.address)

    def save(self, *args, **kwargs):
        self.phone = clean_number_phone(self.phone)
        if self.phone_two:
            self.phone_two = clean_number_phone(self.phone_two)
        super(Client, self).save(*args, **kwargs)


class Inquery(models.Model):
    """Модель для описания заявки от потребителя товаров услуг и.т.д."""
    uuid = models.CharField(editable=False, unique=True, max_length=40, db_index=True)
    owner = models.ForeignKey(User, related_name='inquery_owner', on_delete=models.CASCADE, verbose_name="Создатель заявки")
    designer = models.ForeignKey(User, related_name='inquery_designer', on_delete=models.CASCADE, verbose_name="Менеджер/Дизайнер")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    barter_coefficient = models.BooleanField(default=False, verbose_name="Бартер Да/Нет")
    type_production = models.CharField(max_length=100, verbose_name="Тип изделия")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    source = models.CharField(max_length=100, null=True, blank=True, verbose_name="Источник")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заявки")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения заявки")
    type_pay = models.CharField(max_length=30, choices=inquery_type_pay, null=True, blank=True, verbose_name="Способ оплаты")
    total_amount = models.DecimalField(decimal_places=2, max_digits=11, null=True, blank=True, verbose_name="Итоговая стоимость")
    total_white_goods = models.DecimalField(decimal_places=2, max_digits=11, null=True, blank=True)

    # Статус заявки
    INQUERY_NEW = 'new'
    INQUERY_PAY = 'pay'
    INQUERY_THINK = 'think'
    INQUERY_NOT_PAY = 'not_pay'
    INQUERY_CANCELED = 'canceled'
    INQUERY_REPEAT = 'repeat'

    INQUERY_STATUS_CHOICES = (
        (INQUERY_NEW, u'Новый'),
        (INQUERY_PAY, u'Оплатились'),
        (INQUERY_THINK, u'Думают'),
        (INQUERY_NOT_PAY, u'Отказались'),
        (INQUERY_CANCELED, u'Отменен'),
        (INQUERY_REPEAT, u'Повторная встреча'),
    )
    status = models.CharField(max_length=50, choices=INQUERY_STATUS_CHOICES, verbose_name="Статус")
    # /Статус заявки

    in_work = models.BooleanField(verbose_name=u"Если нужно зафиксировать продажу, но позже ещё прикрепить файлы", default=False)
    history = models.TextField(default={})
    dubl = models.BooleanField(null=True, blank=True, default=False)  # для кнопки "Дубль"
    derivative = models.BooleanField(null=True, blank=True, default=False)  # при создании “первичная/вторичная заявка”
    ko_tz_archived = models.BooleanField(default=False)  # для доп.счетчика у Менеджеров в меню
    to_1c = models.BooleanField(default=False)  # выгружать в 1с или нет

    #  В случае если ведётся продажа изделий, собственного изготовления
    #  И необходима создать чёртёж/дизайн и.т.д.
    #  KO-конструкторский отдел, TZ-тех задание
    KO_TZ_STATUS_CHOICES = (
        # 0
        (0, u'Записи на ТЗ еще не было (либо эта заявка создана до введения нового функционала)'),
        # 1
        (5, u'Перед ТЗ (ответств.дизайнер, КО ожидает ответа от дизайнера)'),
        # 2
        (10, u'Перед ТЗ (ответств.КО, ТЗ ожидает ответа от КО)'),
        # 3
        (15, u'Принят КО (ответств.ТЗ, КО ожидает ответа от ТЗ)'),
        # 4
        (20, u'После ТЗ (ответств.КО, дизайнер ожидает ответа от КО)'),
        # 5
        (25, u'После ТЗ (ответств.дизайнер, КО ожидает ответа от дизайнера)'),
        # 6
        (30, u'На проверке (ответств.КО, дизайнер ожидает ответа от КО)'),
        # 7
        (35, u'Возврат (ответств.дизайнер, КО ожидает от дизайнера исправлений)'),
        # 8
        (40, u'Принято (ответств.дизайнер, ожидается оплата от клиента и подтверждение от дизайнера)'),
        # 9
        (45, u'На сдачу в работу | Оплаченные (ответств.дизайнер, КО ожидает ответа от дизайнера)'),
        # 10
        (50, u'Сданные в работу | Договор на проверке (ответств.КО, от КО ожидается подтверждение)'),
        # 11
        (55, u'Требующие корректировки (ответств.дизайнер, КО ожидает от дизайнера корректировок)'),
        # 12
        (60, u'Повторный замер с дог. (кол должны записать на ТЗ)'),
        # 13
        (65, u'Повторный замер с дог. (ответств.ТЗ, КО ожидает ответа от ТЗ)'),
        # 14
        (70, u'После повторного ТЗ (ответств.КО, дизайнер ожидает от КО проверки)'),
        # 15
        (75, u'Договор в работе'),  # dogovor_v_rabote_arhiv
        # 16
        (80, u'Отмененные ТЗ. КО проверяет, почему ТЗ был удален (кроме "отмененных" и "отказавшихся")'),
    )

     # <МАРШРУТ
    KO_TZ_ROUTE_CHOICES = (
        (0, u'Маршрут заявки не выбран'),
        # (1, u'Оплата до ТЗ'),
        # (2, u'Оплата после ТЗ'),
        # (3, u'Оплата без ТЗ'),
        # (4, u'Оплата с ТЗ'),
    )

    ko_tz_status = models.PositiveSmallIntegerField(choices=KO_TZ_STATUS_CHOICES, default=0)
    ko_tz_route = models.PositiveSmallIntegerField(choices=KO_TZ_ROUTE_CHOICES, default=0)

    def get_ko_tz_status(self):
        """Возвращяет текущий статус заявки"""
        if self.ko_tz_status == 0 and self.ko_tz_route == 3:
            return u'На сдачу в работу (ответств.дизайнер)'
        if self.ko_tz_status == 0 and self.ko_tz_route in (1, 2, 4):
            return u'Ожидание ТЗ (ответств.дизайнер и/или кол, ТЗ и КО ожидают записи на ТЗ от дизайнера или от кол)'
        for n in self.KO_TZ_STATUS_CHOICES:
            if n[0] == self.ko_tz_status:
                return n[1]

    def get_ko_tz_route(self):
        """Возвращяет текущий маршрут заявки"""
        for n in self.KO_TZ_ROUTE_CHOICES:
            if n[0] == self.ko_tz_route:
                return n[1]

    def is_inquery_have_not_deleted_tz(self):
        """Есть активная ТЗ у заявки"""
        return True if self.technicalmeasurement_set.filter(status__in=(0, 1)).order_by('id').last() else False

    def is_inquery_have_active_tz_for_future(self):
        """Есть активная ТЗ у заявки в будущем"""
        active_tz = self.technicalmeasurement_set.filter(status__in=(0, 1)).order_by('id').last()
        return False if not active_tz else active_tz.datetime > timezone.now()

    # /<МАРШРУТ


    objects = models.Manager()
    manager = InqueryManager()
    designers = DesignerManager()

    class Meta:
        # Права доступа, для работы с функц.
        default_permissions = []
        # Роли для пользователей
        permissions = (
            ('is_designer', 'Is designer'),  # дизайнер/продавец/персональный менеджер
            ('is_call_center', 'Is call-center'),   # сотрудник колл-центра
            ('is_chief', 'Is chief'),    # управляющий персонал
            ('is_service', 'Is service man'),   # сервис менеджер/производство/конструктор

            ('vozm_vystavlyat_vozmozhnosti_na_upravlenie_pravami',
             u'Возможность выставлять возможности на управление правами'),
            ('vozm_sozdavat_vsem_novye_zayavki_sobytiya_repin',
             u'Возможность создавать ВСЕМ ДИЗАЙНЕРАМ новые заявки/события, а также удалять любые события'),
            ('vozm_sozdavat_tolko_sebe_novye_zayavki_sobytiya_repin',
             u'Возможность создавать ТОЛЬКО СЕБЕ новые заявки/события, а также удалять свои события'),
            ('vozm_perenaznachat_dizajnerov_v_zayavkah',
             u'Возможность редактировать и удалять любые заявки и переназначать дизайнеров в заявках, ставить статус "Дубль"'),
            ('vozm_sozdavat_novye_tz', u'Возможность создавать новые ТЗ, редактировать и удалять существующие ТЗ'),
            ('vozm_zanimat_bronirovat_vremya_u_tekh_zamershchikov',
             u'Возможность занимать/бронировать время у тех.замерщиков, а также освобождать (удалять соотв. события) такое забронированное время'),
            ('vozm_sozdavat_novyh_sotrudnikov_udalyat_uvolnyat_i_peremeshchat_mezhdu_otdelami',
             u'Возможность создавать новых сотрудников, удалять, увольнять и перемещать между отделами, редактировать почту'),
            ('vozm_skachivat_vse_zayavki_v_xls', u'Возможность скачивать все заявки в XLS'),
            ('vozm_prosmatrivat_i_ispolzovat_stranicu_dlya_rukovoditelya_tz',
             u'Возможность просматривать и использовать страницу для руководителя ТЗ'),
            ('vozm_prosmatrivat_i_raspechatyvat_grafik_tz', u'Возможность просматривать и распечатывать график ТЗ'),
            ('vozm_redaktirovat_grafik_prostavlyat_vyhodnye_v_kalendare_i_v_grafike',
             u'Возможность редактировать график (проставлять выходные в календаре и в графике)'),
            ('vozm_prosmotra_grafika', u'Возможность просмотра графика'),
            ('vozm_prosmotra_statistiki', u'Возможность просмотра статистики'),
            ('vozm_prosmotra_otchetov', u'Возможность просмотра отчетов'),
            ('vozm_prosmatrivat_zayavki_no_ne_redaktirovat_zayavki',
             u'Возможность просматривать заявки (но не редактировать заявки)'),
            ('vozm_prosmatrivat_lyubye_zayavki_no_ne_redaktirovat_zayavki',
             u'Возможность просматривать ЛЮБЫЕ заявки (но не редактировать заявки)'),
            ('vozm_ispolzovaniya_poiska', u'Возможность использования поиска'),
            ('opoveshchenie_o_vhodyashchih_zvonkah_na_telefony_kol_centra',
             u'Оповещение о входящих звонках на телефоны кол центра'),
            ('vozm_skachivat_neoplachen_zayavki_v_xls', u'Возможность скачивать неоплаченные заявки в XLS'),
        )
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __unicode__(self):
        return u"{0} {1}".format(self.designer, self.uuid)

    @property
    def start_datetime(self):
        status = self.inquerystatus_set.filter(Q(status=Inquery.INQUERY_NEW) | Q(status=Inquery.INQUERY_REPEAT)).\
            order_by('id').last()
        return status.start_datetime

    @start_datetime.setter
    def start_datetime(self, value):
        status = self.inquerystatus_set.filter(Q(status=Inquery.INQUERY_NEW) | Q(status=Inquery.INQUERY_REPEAT)).\
            order_by('id').last()
        status.start_datetime = value
        status.save()

    def can_edit(self):
        if self.status == Inquery.INQUERY_NEW or self.status == Inquery.INQUERY_REPEAT:
            return True
        return False

    def can_delete(self):
        if self.status == Inquery.INQUERY_NOT_PAY or self.status == Inquery.INQUERY_CANCELED:
            return False
        return True

    def is_pay(self):
        return self.status == Inquery.INQUERY_PAY

    def get_last_inquery_pay_status(self):
        try:
            return self.inquerystatus_set.filter(hidden=False, status='pay').order_by("-id")[0]
        except IndexError:
            return None

    def get_last_inquery_status(self):
        return self.inquerystatus_set.filter(hidden=False).order_by("-id")[0]

    def get_visible_status(self):
        return self.inquerystatus_set.filter(hidden=False).order_by("-id")

    def get_sorted_history_status(self):
        return self.inquerystatus_set.order_by("-id")

    def get_owner(self):
        owner = self.owner
        return owner.get_full_name()

    def get_last_technical_measurement(self):
        return self.technicalmeasurement_set.order_by('id').last()

    def get_active_technical_measurement(self):
        return self.technicalmeasurement_set.filter(status=0).order_by('id').last()

    def ko_tz_for_1c(self):
        try:
            return self.ko_tz.filter(odin_c=True).order_by('-pk')[:1][0]
        except IndexError:
            return None

    def get_type_pay(self):
        for a in inquery_type_pay:
            if a[0] == self.type_pay:
                return a[1]

    def ko_tz_set(self):
        return self.ko_tz.all().order_by("id")


class InqueryStatus(models.Model):
    """Модель статуса заявки"""
    froze = models.ForeignKey(Inquery, on_delete=models.CASCADE, verbose_name="Заявка")
    call_back = models.DateField(blank=True, null=True)
    start_datetime = models.DateTimeField(blank=True, null=True, verbose_name="Дата замера")
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=Inquery.INQUERY_STATUS_CHOICES, verbose_name="Статус")
    author = models.ForeignKey(User, related_name="author", on_delete=models.CASCADE, verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Дата изменения")
    hidden = models.BooleanField(default=False, verbose_name="Заявка скрыта/активна")
    actual = models.BooleanField(default=True)
    objects = models.Manager()
    manager = InqueryStatusManager()

    def __unicode__(self):
        return u"{0} {1} {2}".format(self.froze, self.status, self.created_at)

    class Meta:
        default_permissions = []
        verbose_name = 'Статус заявки'
        verbose_name_plural = 'Статусы заявок'


class Event(models.Model):
    """Модель события"""
    owner = models.ForeignKey(User, related_name='event_owner', on_delete=models.CASCADE)
    designer = models.ForeignKey(User, related_name='event_designer', on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    canceled = models.BooleanField(default=False)

    objects = models.Manager()
    busy_manager = BusyManager()

    class Meta:
        default_permissions = []

    def is_past(self):
        now = timezone.now()
        date_now = datetime.date(now.year, now.month, now.day)
        start_date = datetime.date(self.start_datetime.year, self.start_datetime.month, self.start_datetime.day)
        if date_now > start_date:
            return True
        return False


class InqueryFile(models.Model):
    """Модель файлы к заявке"""
    froze_status = models.ForeignKey(InqueryStatus, on_delete=models.CASCADE, verbose_name="Статус заявки")
    name = models.CharField(max_length=255, verbose_name="Название файла")
    path = models.CharField(max_length=255, verbose_name="Путь к файлу")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Дата создания")
    is_delete = models.BooleanField(default=False)

    objects = InqueryFileManager()

    class Meta:
        default_permissions = []
        verbose_name = 'Файл заявки'
        verbose_name_plural = 'Файлы заявок'

    def get_absolute_url(self):
        path, filename = os.path.split(self.path)
        return "https://portal-re-formaufa.ru/media/{0}".format(filename)  # fixme: not use absolute url

    def read(self):
        with open(self.path) as fd:
            return base64.b64encode(fd.read())


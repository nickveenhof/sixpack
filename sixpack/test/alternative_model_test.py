import unittest
import fakeredis
import datetime

from sixpack.models import Alternative, Experiment, Client
from sixpack.server import create_app



class TestAlternativeModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.app = create_app()
        # TODO: change this to fake-redis (msetbit script isn't registered with fakeredis currently)
        self.redis = self.app.redis
        self.client_id = 381

    def test_key(self):
        exp = Experiment('show-something', ['yes', 'no'], redis=self.redis)

        alt = Alternative('yes', exp, redis=self.redis)
        key = alt.key()
        self.assertEqual(key, 'sxp:show-something:yes')

    def test_is_valid(self):
        valid = Alternative.is_valid('1')
        self.assertTrue(valid)

        unicode_valid = Alternative.is_valid(u'valid')
        self.assertTrue(unicode_valid)

    def test_is_not_valid(self):
        not_valid = Alternative.is_valid(1)
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid(':123:name')
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid('_123name')
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid('&123name')
        self.assertFalse(not_valid)

    def test_is_control(self):
        exp = Experiment('trololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)
        self.assertTrue(alt.is_control())
        exp.delete()

    def test_experiment(self):
        exp = Experiment('trololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)
        self.assertTrue(alt.is_control())

    def test_participant_count(self):
        pass
        # self.redis.bitcount.return_value = 0

        # alt = Alternative('yes', 'show-something', self.redis)
        # count = alt.participant_count()

        # key = _key("participation:{0}:{1}".format(alt.experiment_name, alt.name))
        # self.redis.bitcount.assert_called_once_with(key)
        # self.assertTrue(isinstance(count, Number))

        # self.redis.reset_mock()

    def test_conversion_count(self):
        pass
        # self.redis.reset_mock()
        # self.redis.bitcount.return_value = 0

        # alt = Alternative('yes', 'show-something', self.redis)
        # count = alt.completed_count()

        # key = _key("c:{0}/1:{1}".format(alt.experiment_name, alt.name))
        # self.redis.bitcount.assert_called_once_with(key)
        # self.assertTrue(isinstance(count, Number))

        # self.redis.reset_mock()

    # TODO Test this
    def test_record_participation(self):
        pass
        # alt = Alternative('yes', 'show-something', self.redis)
        # alt.record_participation(self.client_id)

        # key = _key("participation:{0}:{1}".format(alt.experiment_name, alt.name))
        # self.redis.setbit.assert_called_once_with(key, self.client_id, 1)

    def test_record_conversion(self):
        pass
        # client = Client('xyz', self.redis)
        # alt = Alternative('yes', 'show-something', self.redis)
        # alt.record_conversion(client)

        # key = _key("conversion:{0}:{1}".format(alt.experiment_name, alt.name))
        # self.redis.setbit.assert_called_once_with(key, self.client_id, 1)

    def test_total_reward(self):
        client = Client(10, redis=self.redis)

        exp = Experiment('trolololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)

        client = Client(10, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 42)

        client = Client(20, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 21)

        self.assertEqual(63, alt.total_reward())

    def test_average_reward_single(self):
        client = Client(10, redis=self.redis)

        exp = Experiment('trololololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 42)

        self.assertEqual(42, alt.average_reward())

    def test_average_reward_all_converted(self):
        exp = Experiment('trolololololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)

        client = Client(10, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 42)

        client = Client(20, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 12)

        self.assertEqual(27, alt.average_reward())

    def test_average_reward_some_not_converted(self):
        exp = Experiment('trololololololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)

        for i in range(10):
            client = Client(i, redis=self.redis)
            alt.record_participation(client)
            alt.record_conversion(client, 42)

        for i in range(10):
            client = Client(i+10, redis=self.redis)
            alt.record_participation(client)

        for i in range(10):
            client = Client(i+20, redis=self.redis)
            alt.record_participation(client)
            alt.record_conversion(client, 12)

        # (10 * 42 + 10 * 0 + 10 * 12) / 30
        self.assertEqual(18, alt.average_reward())

    def test_rewards_by_day(self):
        exp = Experiment('rewardsbyday', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)

        dt = datetime.datetime(2015, 10, 1)
        client = Client(0, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 12.10, dt)

        dt = datetime.datetime(2015, 11, 1)
        client = Client(1, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 12.10, dt)

        rewards = alt.reward_by_day()
        self.assertEqual(2, len(rewards))
        self.assertEqual(12.10, rewards['2015-10-01'])
        self.assertEqual(12.10, rewards['2015-11-01'])

    def test_rewards_by_month(self):
        exp = Experiment('rewardsbymonth', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)

        for i in range(10):
            dt = datetime.datetime(2015, 10, i + 1)
            client = Client(i, redis=self.redis)
            alt.record_participation(client)
            alt.record_conversion(client, 12.10, dt)

        dt = datetime.datetime(2015, 11, 1)
        client = Client(11, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 12.10, dt)

        rewards = alt.reward_by_month()
        self.assertEqual(2, len(rewards))
        self.assertEqual(12.10, rewards['2015-11'])
        self.assertEqual(121.0, rewards['2015-10'])

    def test_rewards_by_year(self):
        exp = Experiment('rewardsbyyear', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)

        for i in range(10):
            dt = datetime.datetime(2015, 10, i + 1)
            client = Client(i, redis=self.redis)
            alt.record_participation(client)
            alt.record_conversion(client, 12.10, dt)

        dt = datetime.datetime(2014, 10, 1)
        client = Client(11, redis=self.redis)
        alt.record_participation(client)
        alt.record_conversion(client, 12.10, dt)

        rewards = alt.reward_by_year()
        self.assertEqual(2, len(rewards))
        self.assertEqual(12.10, rewards['2014'])
        self.assertEqual(121.0, rewards['2015'])

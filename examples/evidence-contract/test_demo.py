import unittest
from demo import SOURCES, audit, host_execute, run


class EvidenceContractTests(unittest.TestCase):
    def test_valid_fixture_accepted(self):
        self.assertTrue(run('valid')['audit']['accepted'])

    def test_failed_source_cannot_support_claim(self):
        self.assertIn('source_not_verified:s3', run('forged')['audit']['reasons'])

    def test_injected_observation_cannot_change_host_authority(self):
        result = run('injection')
        self.assertEqual(result['state'], {})
        self.assertIn('operation_out_of_scope', result['audit']['reasons'])

    def test_unknown_operation_does_not_change_state(self):
        state = {}
        self.assertFalse(host_execute({'operation': 'delete_files'}, state, []))
        self.assertEqual(state, {})

    def test_successful_tool_result_is_not_sufficient(self):
        proposal = {'operation': 'write_summary', 'status': 'completed', 'citations': []}
        self.assertFalse(audit(proposal, True, SOURCES)['accepted'])

    def test_fabricated_quote_rejected(self):
        proposal = run('valid')['state']['summary']
        proposal['citations'][0]['quote'] = '审批保证万无一失'
        self.assertIn('quote_not_in_source:s1', audit(proposal, True, SOURCES)['reasons'])

    def test_duplicate_source_does_not_meet_coverage(self):
        proposal = run('valid')['state']['summary']
        proposal['citations'] = [proposal['citations'][0]] * 2
        self.assertIn('missing_verified_source:s2', audit(proposal, True, SOURCES)['reasons'])

    def test_unknown_source_rejected(self):
        proposal = run('valid')['state']['summary']
        proposal['citations'].append({'source': 'unknown', 'quote': '可信'})
        self.assertIn('source_not_verified:unknown', audit(proposal, True, SOURCES)['reasons'])


if __name__ == '__main__':
    unittest.main()

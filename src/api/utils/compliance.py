import logging

def check_device_compliance(device, report):
    """
    Check the compliance of a device and return both the compliance status and detailed rule results.
    """
    policy_rulesets = device.rulesets.all()
    policy_rulesets = list(policy_rulesets)
    
    logging.debug('Policy rulesets for device %s: %s', device, policy_rulesets)
    
    compliant = True
    evaluated_rulesets = []
    
    for policy_ruleset in policy_rulesets:
        ruleset_dict = {
            'id': policy_ruleset.id,
            'name': policy_ruleset.name,
            'description': policy_ruleset.description,
            'rules': []
        }
        
        ruleset_compliant = True
        for rule in policy_ruleset.rules.all():
            rule_compliant = rule.evaluate(report)
            ruleset_dict['rules'].append({
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'enabled': rule.enabled,
                'alert': rule.alert,
                'compliant': rule_compliant
            })
            if not rule_compliant:
                ruleset_compliant = False
        
        ruleset_dict['compliant'] = ruleset_compliant
        evaluated_rulesets.append(ruleset_dict)
        
        if not ruleset_compliant:
            compliant = False
    
    return compliant, evaluated_rulesets


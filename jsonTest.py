import json

# Your JSON data
json_data = """
{
    "Home": {
        "label": "L11 Home",
        "url": "/home",
        "protected": false,
        "allowed_roles": ["Admin", "Authority", "Employee", "Manager", "Guest"],
        "submenus": {
            "About us": {
                "label": "L12 About us",
                "url": "/home/aboutus_1",
                "protected": false,
                "allowed_roles": ["Admin", "Authority", "Employee", "Manager", "Guest"]
            },
            "History": {
                "label": "History",
                "url": "/home/history",
                "protected": false,
                "allowed_roles": ["Admin", "Authority", "Employee", "Manager", "Guest"]
            },
            "Mission": {
                "label": "Mission",
                "url": "/home/mission",
                "protected": false,
                "allowed_roles": ["Admin", "Authority", "Employee", "Manager", "Guest"]
            },
            "Site map": {
                "label": "Site map",
                "url": "/home/site_map",
                "protected": false,
                "allowed_roles": ["Admin", "Authority", "Employee", "Manager", "Guest"]
            }
        }
    },
    "Dashboard": {
        "label": "Dashboard",
        "url": "/dashboard",
        "protected": true,
        "allowed_roles": ["Admin", "Authority", "Employee", "Manager"],
        "submenus": {
            "Company": {
                "label": "User Area",
                "url": "/dashboard/company",
                "protected": true,
                "allowed_roles": ["Admin", "Employee", "Manager"],
                "submenus": {
                    "Audit": {
                        "label": "Audit",
                        "url": "/dashboard/company/dashboard_audit",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    },
                    "Controls": {
                        "label": "Authority Controls",
                        "url": "/dashboard/company/dashboard_controls",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    },
                    "Remediation": {
                        "label": "Remediation",
                        "url": "/dashboard/company/dashboard_remediation",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    },
                    "Compliance": {
                        "label": "Compliance",
                        "url": "/dashboard/company/dashboard_compliance",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    },
                    "Proceedings": {
                        "label": "Proceedings",
                        "url": "/dashboard/company/dashboard_proceedings",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    },
                    "Deadlines": {
                        "label": "Deadlines",
                        "url": "/dashboard/company/dashboard_deadlines",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    }
                }
            },
            "Authority": {
                "label": "Authority",
                "url": "/dashboard/authority/dashboard_a1",
                "protected": true,
                "allowed_roles": ["Admin", "Authority"],
                "submenus": {
                    "Area 1": {
                        "label": "L223 Area 1",
                        "url": "/dashboard/authority/dashboard_a1",
                        "protected": true,
                        "allowed_roles": ["Admin", "Authority"]
                    },
                    "Area 2": {
                        "label": "Area 2",
                        "url": "/dashboard/authority/dashboard_a2",
                        "protected": true,
                        "allowed_roles": ["Admin", "Authority"]
                    },
                    "Area 3": {
                        "label": "Area 3",
                        "url": "/dashboard/authority/dashboard_a3",
                        "protected": true,
                        "allowed_roles": ["Admin", "Authority"]
                    }
                }
            },
            "ILM": {
                "label": "ILM",
                "url": "/dashboard/ILM/dashboard_m1",
                "protected": true,
                "allowed_roles": ["Admin"],
                "submenus": {
                    "Clients": {
                        "label": "Clients",
                        "url": "/dashboard/company/dashboard_audit",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    },
                    "Audit": {
                        "label": "Audit",
                        "url": "/dashboard/company/dashboard_audit",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    },
                    "Controls": {
                        "label": "Authority Controls",
                        "url": "/dashboard/company/dashboard_controls",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    },
                    "Remediation": {
                        "label": "Remediation",
                        "url": "/dashboard/company/dashboard_remediation",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    },
                    "Compliance": {
                        "label": "Compliance",
                        "url": "/dashboard/company/dashboard_compliance",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    },
                    "Proceedings": {
                        "label": "Proceedings",
                        "url": "/dashboard/company/dashboard_proceedings",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    },
                    "Deadlines": {
                        "label": "Deadlines",
                        "url": "/dashboard/company/dashboard_deadlines",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    },
                    "System Setup": {
                        "label": "System Setup",
                        "url": "/dashboard/company/dashboard_system_setup",
                        "protected": true,
                        "allowed_roles": ["Admin"]
                    }
                }
            }
        }
    },
    "Workflow": {
        "label": "L21 Workflow",
        "url": "/workflow",
        "protected": true,
        "allowed_roles": ["Admin", "Employee", "Manager"],
        "submenus": {
            "Main": {
                "label": "L212 Main",
                "url": "/workflow/main",
                "protected": true,
                "allowed_roles": ["Admin", "Employee", "Manager"],
                "submenus": {
                    "Workflow A": {
                        "label": "L213 Workflow A",
                        "url": "/workflow/main/workflow_a",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"],
                        "submenus": {
                            "Sub Sub 1": {
                                "label": "Work A A 1",
                                "url": "workflow/main/workflow_a/workaa1",
                                "protected": true,
                                "allowed_roles": ["Admin", "Employee", "Manager"]
                            }
                        }
                    }
                },
                "Workflow B": {
                    "label": "Workflow B",
                    "url": "/workflow/main/workflow_b",
                    "protected": true,
                    "allowed_roles": ["Admin", "Employee", "Manager"]
                }
            },
            "Control Areas": {
                "label": "L222 Control Areas",
                "url": "/workflow/control-areas",
                "protected": true,
                "allowed_roles": ["Admin", "Employee", "Manager"],
                "submenus": {
                    "Area 1": {
                        "label": "L223 Area 1",
                        "url": "/workflow/control_areas/area_1",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    },
                    "Area 2": {
                        "label": "Area 2",
                        "url": "/workflow/control_areas/area_2",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    },
                    "Area 3": {
                        "label": "Area 3",
                        "url": "/workflow/control_areas/area_3",
                        "protected": true,
                        "allowed_roles": ["Admin", "Employee", "Manager"]
                    }
                }
            },
            "Sub-submenu 1": {
                "label": "L2321 Sub-submenu 1",
                "url": "/workflow/sub-submenu-1",
                "protected": true,
                "allowed_roles": ["Admin", "Employee", "Manager"]
            },
            "Sub-submenu 2": {
                "label": "L242 Sub-submenu 2",
                "url": "/workflow/sub-submenu-2",
                "protected": true,
                "allowed_roles": ["Admin", "Employee", "Manager"]
            }
        }
    },
    "Blog": {
        "label": "Blog",
        "url": "/blog/blog",
        "protected": true,
        "allowed_roles": ["Admin", "Employee", "Manager"]
    },
    "Contacts": {
        "label": "Contact",
        "url": "/contact",
        "protected": False,
        "allowed_roles": ["Admin", "Employee", "Manager", "Authority", "Guest"],
        "submenus": {
            "Mail": {
                "label": "eMail",
                "url": "/contact/email",
                "protected": False,
                "allowed_roles": ["Admin", "Employee", "Manager", "Authority", "Guest"]
            },
            "Signup": {
                "label": "Phone",
                "url": "/contact/phone",
                "protected": False,
                "allowed_roles": ["Admin", "Employee", "Manager", "Authority", "Guest"]
            }
        }
    },
    "Access": {
        "label": "Access",
        "url": "/access",
        "protected": false,
        "allowed_roles": ["Admin", "Employee", "Manager", "Authority", "Guest"],
        "submenus": {
            "Login": {
                "label": "Login",
                "url": "/access/login",
                "protected": false,
                "allowed_roles": ["Admin", "Employee", "Manager", "Authority", "Guest"]
            },
            "Signup": {
                "label": "Signup",
                "url": "/access/signup",
                "protected": false,
                "allowed_roles": ["Admin", "Employee", "Manager", "Authority", "Guest"]
            },
            "Logout": {
                "label": "Logout",
                "url": "/access/logout",
                "protected": true,
                "allowed_roles": ["Admin", "Employee", "Manager", "Authority", "Guest"]
            }
        }
    }
}
"""

# Load JSON data in chunks
chunk_size = 1000  # You can adjust this value
start = 0

while start < len(json_data):
    chunk = json_data[start:start + chunk_size]

    try:
        data = json.loads(chunk)
    except json.JSONDecodeError as e:
        print(f"Error loading JSON: {e}")
        print("Problematic JSON chunk:")
        print(chunk)
        break

    start += chunk_size


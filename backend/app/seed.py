from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Institution, User, Case, TimelineEvent
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Institution).count() > 0:
            print("Database already seeded.")
            return

        print("Seeding database...")

        # 1. Seed Users
        users_data = [
            ("rb_admin", "password123", "RB", "Regulation Bureau", "All"),
            ("pgrc_admin", "password123", "PGRC", "PGRC", "All"),
            ("cell_admin", "password123", "Cell", "Academic Cell", "All"),
            ("ro_north", "password123", "RegionalOffice", "Regional Office North", "North"),
            ("ro_west", "password123", "RegionalOffice", "Regional Office West", "West"),
            ("ro_south", "password123", "RegionalOffice", "Regional Office South", "South"),
            ("senior_mgmt", "password123", "SeniorManagement", "Executive Board", "All"),
            ("competent_authority", "password123", "CompetentAuthority", "Director Office", "All"),
        ]

        for uname, pwd, role, bureau, region in users_data:
            user = User(
                id=uname,
                username=uname,
                hashed_password=pwd_context.hash(pwd),
                role=role,
                bureau_cell=bureau,
                region=region,
                is_active=True
            )
            db.add(user)

        # 2. Seed Institutions (~30 institutions, including messy names for matching tests)
        institutions_data = [
            ("1-1111111", "XYZ College of Engineering", "123 Tech Park Road, Pune", "West", "411001"),
            ("1-1111199", "XYZ Engg College, Pune", "123 Tech Park Rd, Pune", "West", "411001"), # Messy variant for testing matcher
            ("1-2222222", "ABC Institute of Technology", "45 Industrial Area, Bangalore", "South", "560001"),
            ("1-3333333", "National Institute of Management", "78 Civil Lines, Delhi", "North", "110001"),
            ("1-4444444", "Global College of Pharmacy", "12 Ring Road, Hyderabad", "South", "500032"),
            ("1-5555555", "Sunrise University", "99 University Avenue, Jaipur", "North", "302017"),
            ("1-6666666", "Apex Institute of Technology", "88 IT Hub, Chennai", "South", "600113"),
            ("1-7777777", "Pioneer College of Engineering", "14 Station Road, Mumbai", "West", "400001"),
            ("1-8888888", "Modern Institute of Science", "56 Lake View, Kolkata", "East", "700001"),
            ("1-9999999", "Vision School of Architecture", "33 Heritage Lane, Ahmedabad", "West", "380015"),
            ("1-1010101", "Elite Technical Campus", "10 Residency Road, Lucknow", "North", "226001"),
            ("1-1212121", "Dynamic College of Engineering", "5 Orchard Road, Pune", "West", "411002"),
            ("1-1313131", "Sterling Institute of Management", "9 Marine Drive, Kochi", "South", "682011"),
            ("1-1414141", "Centennial University", "77 Hill Top, Shimla", "North", "171001"),
            ("1-1515151", "Prime Institute of Technology", "22 Sector 4, Chandigarh", "North", "160017"),
            ("1-1616161", "Horizon College of Engineering", "88 Bypass Road, Bhopal", "Central", "462001"),
            ("1-1717171", "Vanguard Institute of Technology", "19 MG Road, Patna", "East", "800001"),
            ("1-1818181", "Summit University", "41 Ridge Road, Dehradun", "North", "248001"),
            ("1-1919191", "Titan College of Engineering", "63 Industrial Estate, Coimbatore", "South", "641021"),
            ("1-2020201", "Galaxy Institute of Management", "55 Airport Road, Nagpur", "West", "440005"),
            ("1-2121212", "Beacon Technical Institute", "12 Canal Bank, Surat", "West", "395007"),
            ("1-2222223", "Alpha College of Engineering", "90 Tech Zone, Noida", "North", "201301"),
            ("1-2323232", "Omega Institute of Technology", "11 Temple Street, Madurai", "South", "625001"),
            ("1-2424242", "Stellar University", "44 Star Avenue, Indore", "Central", "452001"),
            ("1-2525252", "Paramount College of Pharmacy", "21 Health Hub, Visakhapatnam", "South", "530003"),
            ("1-2626262", "Zenith Institute of Technology", "7 College Road, Vadodara", "West", "390001"),
            ("1-2727272", "Nexus College of Engineering", "39 Silicon Valley, Bhubaneswar", "East", "751024"),
            ("1-2828282", "Venture University", "66 Startup Park, Jaipur", "North", "302015"),
            ("1-2929292", "Imperial Institute of Management", "18 Royal Palace, Mysore", "South", "570001"),
            ("1-3030303", "Pathway College of Engineering", "50 Highway Road, Nagpur", "West", "440001")
        ]

        for pid, name, addr, reg, pin in institutions_data:
            inst = Institution(permanent_id=pid, name=name, address=addr, region=reg, pincode=pin)
            db.add(inst)

        db.commit()

        # 3. Seed ~150 Cases across RB, PGRC, Academic Cell, Finance Cell
        categories = ["Faculty Shortage", "Fee Dispute", "Infrastructure Deficiency", "Ragging Complaint", "Non-payment of Salary", "Capitation Fee", "Unapproved Course"]
        bureaus = ["Regulation Bureau", "PGRC", "Academic Cell", "Finance Cell"]
        statuses = ["Pending", "Under Process", "Disposed", "Transferred"]
        officers = ["Dr. Sharma", "Mr. Verma", "Ms. Iyer", "Dr. Rao", "Mr. Gupta", "Ms. Nair"]

        case_counter = 1000
        for i, (pid, name, _, _, _) in enumerate(institutions_data):
            # Create 4 to 6 cases per institution across different bureaus
            num_cases = 5
            for c_idx in range(num_cases):
                case_id = f"AICTE-2026-{case_counter}"
                case_counter += 1

                bureau = bureaus[(i + c_idx) % len(bureaus)]
                category = categories[(i + c_idx) % len(categories)]
                status = statuses[(c_idx) % len(statuses)]
                officer = officers[(i + c_idx) % len(officers)]

                # Make sure at least two cases for Institution A (1-1111111) are open in different bureaus to trigger the overlap radar demo
                if pid == "1-1111111" and c_idx == 0:
                    bureau = "Regulation Bureau"
                    status = "Pending"
                    category = "Faculty Shortage"
                elif pid == "1-1111111" and c_idx == 1:
                    bureau = "PGRC"
                    status = "Pending"
                    category = "Faculty Shortage"

                case_item = Case(
                    case_id=case_id,
                    institution_id=pid,
                    source_bureau=bureau,
                    category=category,
                    description=f"Complaint regarding {category.lower()} reported at {name}. Immediate inspection and verification required.",
                    status=status,
                    current_bureau=bureau,
                    assigned_officer=officer,
                    last_action="Initial grievance logging and review",
                    next_action_required="Dispatch committee for on-site verification",
                    expected_disposal_date=datetime.utcnow() + timedelta(days=15),
                    created_at=datetime.utcnow() - timedelta(days=c_idx*3)
                )
                db.add(case_item)

                # Add initial timeline event
                timeline_event = TimelineEvent(
                    case_id=case_id,
                    officer=officer,
                    bureau_cell=bureau,
                    timestamp=datetime.utcnow() - timedelta(days=c_idx*3),
                    remarks=f"Case registered in {bureau}. Assigned to {officer}.",
                    attached_documents="initial_complaint.pdf",
                    transfer_escalation_info=None
                )
                db.add(timeline_event)

        db.commit()
        print("Database seeded successfully with institutions, users, and cases.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

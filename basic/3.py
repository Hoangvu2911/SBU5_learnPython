def grade_define(score):
    if score >= 90 and score < 100:
        return 'A'
    elif score >= 80 and score < 90:
        return 'B'
    elif score >= 70 and score < 80:
        return 'C'
    elif score >= 60 and score < 70:
        return 'D'
    elif score >= 0 and score < 60:
        return 'F'
    else:
        return 'Invalid score'

def test_grade_define():
    assert grade_define(90) == 'A'
    assert grade_define(85) == 'B'
    assert grade_define(105) == 'Invalid score'
    assert grade_define(-4) == 'Invalid score'

def leaf_year(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def test_leaf_year():
    assert leaf_year(2000) == True
    assert leaf_year(2001) == False
    assert leaf_year(2004) == True
    assert leaf_year(2026) == False
    assert leaf_year(2028) == True

if __name__ == "__main__":
    score = int(input("Enter your score: "))
    print(grade_define(score))
    year = int(input("Enter a year: "))
    print(leaf_year(year))
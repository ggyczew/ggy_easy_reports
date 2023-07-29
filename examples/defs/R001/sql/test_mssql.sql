select u.name, u.age, ul.level, l.language, l.difficulty
from easy_reports.dbo.er_test_users u
left join easy_reports.dbo.er_test_user_language ul on (ul.user_id = u.id)
left join easy_reports.dbo.er_test_languages l on (l.id = ul.language_id)
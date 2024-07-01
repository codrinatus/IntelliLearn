import matplotlib.pyplot as plt

years = [2018, 2019, 2020, 2021]
duolingo_users = [300, 385, 500, 575]  # in millions
coursera_users = [35, 44, 71, 92]  # in millions

fig, ax = plt.subplots(figsize=(12, 8))

ax.plot(years, duolingo_users, marker='o', color='green', linestyle='-', linewidth=2, markersize=8, label='Duolingo')
ax.plot(years, coursera_users, marker='o', color='blue', linestyle='-', linewidth=2, markersize=8, label='Coursera')

ax.set_xlabel('Year', fontsize=14, color='black')
ax.set_ylabel('Number of Users (in millions)', fontsize=14, color='black')
ax.set_title('Growth in Users of Online Education Platforms (2018-2021)', fontsize=16, color='black')
ax.legend(fontsize=12, facecolor='white')
ax.grid(True, linestyle='--', alpha=0.7)

ax.set_xticks(years)
ax.set_xticklabels(years, fontsize=12, color='black')

for i, txt in enumerate(duolingo_users):
    ax.annotate(f'{txt}M', (years[i], duolingo_users[i]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color='green')
for i, txt in enumerate(coursera_users):
    ax.annotate(f'{txt}M', (years[i], coursera_users[i]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color='blue')

fig.patch.set_facecolor('white')
ax.set_facecolor('white')

plt.tight_layout()
plt.savefig("online_education_growth_high_res.png", dpi=300)
plt.show()

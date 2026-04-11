import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

arr = np.array([1,2,3,4,5])
print(np.mean(arr))
print(np.std(arr))

x = np.linspace(0,1,10)
y = np.square(x)

plt.plot(x,y,'r-*')
plt.xlim([-1,2])
plt.ylim([-0.5,1.5])
plt.xlabel('x')
plt.ylabel('y')
plt.title('x vs y')
plt.legend(['Square of x'])
plt.grid(True)
#plt.show()
# 
data = {
    "name"  : ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "score" : [85, 92, 78, 95, 60],
    "grade" : ["B", "A", "C", "A", "D"],
    "passed": [True, True, True, True, False]
}
df = pd.DataFrame(data)
print(df)
print(df.loc[df['passed']])
print(df["score"].describe()) 

data = np.random.normal(70, 10, 1000)   # 1000 random scores, mean=70, std=10
plt.figure(figsize=(8, 4))
plt.hist(data, bins=30, color="steelblue", edgecolor="white")
plt.title("Score Distribution")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.show()

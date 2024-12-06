define dso_local i32 @sum(i32 noundef %1, i32 noundef %2) #0 {
	%4 = alloca i32, align 4
	store i32 %1, ptr %4, align 4
	%5 = alloca i32, align 4
	store i32 %2, ptr %5, align 4
	%6 = load i32, ptr %4, align 4
	%7 = load i32, ptr %5, align 4
	%8 = mul nsw i32 %6, %7
	ret i32 %8
}

define dso_local i32 @main() #1 {
	%2 = call i32 @sum(i32 noundef 2, i32 noundef 2)
	ret i32 %2
}


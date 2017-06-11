def word_shape(s):
	r = ''
	for c in s:
		if c.isalpha():
			if c.isupper():
				r += 'X'
			else:
				r += 'x'
		elif c.isdigit():
			r += 'd'
		else:
			r += c
	r_copy = r[0]
	for c in r[1:]:
		if r_copy[-1] != c:
			r_copy += c
	return r_copy
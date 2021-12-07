CREATE TABLE indoc_vre.user_key (
	id SERIAL NOT NULL, 
	user_geid VARCHAR, 
	public_key VARCHAR, 
	key_name VARCHAR, 
	is_sandboxed BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT unique_key UNIQUE (key_name, user_geid, is_sandboxed), 
	UNIQUE (id)
)

CHEF_SOLO_CMD=vendor/ruby/1.9.1/bin/chef-solo

.PHONY: deploy

deploy:
	bundle exec librarian-chef install --clean
	bundle exec chef-solo -c solo.rb -j node.json

.PHONY: install

install: $(CHEF_SOLO_CMD)

$(CHEF_SOLO_CMD):
	sudo gem install bundler
	bundle install --local --path vendor

.PHONY: clean

clean:
	rm -r vendor/ruby

# -*- coding: utf-8 -*-
from base64 import b85encode

__author__ = 'Xavier ROSSET'


x = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu lorem elementum, scelerisque erat a, euismod mi. Donec eleifend neque id commodo facilisis. Sed at odio tempus, aliquam lorem eu, tempor erat. " \
    "Integer lobortis imperdiet magna vel suscipit. Integer elementum eros nec justo viverra molestie. Sed id blandit nibh. Curabitur tempus gravida consequat. In interdum nisl a lectus efficitur, aliquet " \
    "pellentesque sem lobortis. Duis vitae ipsum at mauris congue pellentesque sit amet vitae diam. Aenean pharetra mi ac metus lacinia semper. Curabitur tempor, justo quis molestie consectetur, sem metus semper " \
    "metus, sed consectetur nulla arcu ut leo. Etiam elementum mauris eget massa eleifend, ac tristique massa molestie. " \
    "Etiam pellentesque scelerisque porttitor. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In sed accumsan ipsum, vel ultricies metus. Morbi a lectus euismod, porttitor " \
    "nibh id, tincidunt nisi. Phasellus sagittis lacus magna, porttitor efficitur eros congue ut. Phasellus hendrerit consequat metus vel dictum. Vivamus faucibus aliquet mollis. Aenean eleifend eu ipsum a " \
    "aliquet. Etiam iaculis nec turpis eu congue. Sed porta, justo consectetur vulputate tincidunt, tortor velit posuere nunc, ultrices facilisis justo est eu diam. Nunc turpis turpis, porttitor non blandit " \
    "nec, sollicitudin et dui. Fusce commodo lorem non arcu porta fermentum. Maecenas ante libero, porta eu feugiat nec, tincidunt sed sem. Phasellus tristique tristique sem, interdum condimentum est lacinia ut. " \
    "Integer finibus est at elit lobortis, in finibus velit venenatis. " \
    "Aenean tortor ligula, placerat in facilisis ut, tincidunt pretium lorem. Suspendisse quis lectus mattis, mattis enim faucibus, pellentesque lectus. Sed eget feugiat est. Morbi varius nibh in vulputate " \
    "tristique. Phasellus nec malesuada lorem. Suspendisse aliquet convallis tincidunt. Pellentesque fringilla iaculis enim at sollicitudin. Suspendisse fringilla metus in pulvinar vehicula. Vivamus dignissim est " \
    "nisl, non tempor urna tempus a. Aenean eu dolor sapien. Praesent eu augue eget neque auctor hendrerit quis vitae metus. Vivamus non nisl nec turpis lobortis pretium. Quisque vel mi felis. Suspendisse at " \
    "mauris nec purus interdum varius. Duis quis neque at magna volutpat facilisis nec a nulla. " \
    "Sed finibus et nisl eget tempus. Curabitur malesuada dignissim purus, a lobortis lectus varius ac. Sed efficitur nunc lacus. Integer sollicitudin nulla eget mauris finibus, id dignissim nisi lacinia. Etiam " \
    "sit amet mi fermentum, tristique libero at, sagittis quam. Nulla facilisis congue laoreet. Cras sollicitudin, enim sit amet euismod semper, eros sapien aliquam quam, sed rutrum turpis lorem eget sapien. " \
    "Vivamus ultrices sed ante nec tincidunt. Interdum et malesuada fames ac ante ipsum primis in faucibus. Nullam a nisl vehicula nibh varius venenatis sit amet et lorem. Vivamus lobortis nisi at fringilla " \
    "mollis. Fusce nec fringilla leo. Quisque malesuada eu est sed suscipit. " \
    "Donec et diam dictum, ornare nibh et, efficitur velit. Integer eget elit vel tortor aliquam finibus sit amet ac urna. Aenean ut eros iaculis, tempor eros malesuada, euismod dui. Etiam molestie quis tortor in " \
    "tincidunt. Cras lobortis dictum neque, nec commodo augue interdum ullamcorper. Integer vitae laoreet sem. Quisque elementum sagittis volutpat. Duis placerat, nulla at fermentum convallis, risus risus " \
    "tristique lacus, sit amet viverra dolor enim ac lorem. "

print(b85encode(x.encode(encoding="UTF_8")))

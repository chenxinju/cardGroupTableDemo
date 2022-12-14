//
//  GroupShadowTableView.h
//  cardGroupTableDemo
//
//  Created by iOS1 on 2022/10/24.
//  Copyright © 2022 Developer. All rights reserved.
//tableview 分组加阴影 圆角

#import <UIKit/UIKit.h>

@class GroupShadowTableView;
@protocol GroupShadowTableViewDelegate <NSObject>

@optional
- (void)groupShadowTableView:(GroupShadowTableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath;

- (CGFloat)groupShadowTableView:(GroupShadowTableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath;

//头部高度
- (CGFloat)groupShadowTableView:(GroupShadowTableView *)tableView heightForHeaderInSection:(NSInteger)section;

//头部view
- (UIView *)groupShadowTableView:(GroupShadowTableView *)tableView viewForHeaderInSection:(NSInteger)section;

//尾部高度
- (CGFloat)groupShadowTableView:(GroupShadowTableView *)tableView heightForFooterInSection:(NSInteger)section;

//尾部view
- (UIView *)groupShadowTableView:(GroupShadowTableView *)tableView viewForFooterInSection:(NSInteger)section;


- (BOOL)groupShadowTableView:(GroupShadowTableView *)tableView canSelectAtSection:(NSInteger)section;

@end

@protocol GroupShadowTableViewDataSource <NSObject>
@optional
- (NSInteger)numberOfSectionsInGroupShadowTableView:(GroupShadowTableView *)tableView;

@required

- (NSInteger)groupShadowTableView:(GroupShadowTableView *)tableView numberOfRowsInSection:(NSInteger)section;

- (UITableViewCell *)groupShadowTableView:(GroupShadowTableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath;

@end

@interface GroupShadowTableView : UITableView
/**
 是否显示分割线  默认YES
 */
@property (nonatomic,assign) BOOL showSeparator;

@property (nonatomic,weak) IBOutlet id <GroupShadowTableViewDelegate> groupShadowDelegate;

@property (nonatomic,weak) IBOutlet id <GroupShadowTableViewDataSource> groupShadowDataSource;

@property (nonatomic,copy) NSInteger (^numberOfSectionsInGroupShadowTableView)(GroupShadowTableView *tableView);

@property (nonatomic,copy) NSInteger (^numberOfRowsInSection)(GroupShadowTableView *tableView,NSInteger section);

@property (nonatomic,copy) CGFloat (^heightForRowAtIndexPath)(GroupShadowTableView *tableView,NSIndexPath *indexPath);

@property (nonatomic,copy) UITableViewCell * (^cellForRowAtIndexPath)(GroupShadowTableView *tableView,NSIndexPath *indexPath);

@property (nonatomic,copy) void (^didSelectRowAtIndexPath)(GroupShadowTableView *tableView,NSIndexPath *indexPath);

@end
